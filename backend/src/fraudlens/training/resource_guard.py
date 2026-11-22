"""Subprocess watchdog for the local, protocol-bounded experiment."""

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


class ResourceLimitError(RuntimeError):
    """The experiment stopped before a complete output was published."""


def free_disk_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


def _require_memory_monitor() -> None:
    if os.name != 'nt':
        try:
            subprocess.run(['ps', '-axo', 'pid=,ppid=,rss='],
                           capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            raise ResourceLimitError(f'memory monitor unavailable: {error}') from error


def process_tree_rss_bytes(root_pid: int) -> int:
    """Sum resident bytes for the worker and descendants; ps RSS is in KiB."""
    if os.name == 'nt':
        # Windows has no portable ps command. The worker is the only Python
        # process in the current LightGBM path; fail closed if it cannot be read.
        import ctypes

        class MemoryCounters(ctypes.Structure):
            _fields_ = [
                ('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong),
                ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
                ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t),
                ('PrivateUsage', ctypes.c_size_t),
            ]

        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        open_process = ctypes.windll.kernel32.OpenProcess
        open_process.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
        open_process.restype = ctypes.c_void_p
        handle = open_process(0x1000 | 0x0400, False, root_pid)
        if not handle:
            raise ResourceLimitError('cannot inspect worker memory')
        try:
            get_info = ctypes.windll.psapi.GetProcessMemoryInfo
            get_info.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong)
            if not get_info(
                handle, ctypes.byref(counters), ctypes.sizeof(counters)
            ):
                raise ResourceLimitError('cannot inspect worker memory')
            return int(counters.WorkingSetSize)
        finally:
            close_handle = ctypes.windll.kernel32.CloseHandle
            close_handle.argtypes = (ctypes.c_void_p,)
            close_handle(handle)
    result = subprocess.run(
        ['ps', '-axo', 'pid=,ppid=,rss='], capture_output=True, text=True, check=True,
    )
    children: dict[int, list[int]] = {}
    rss: dict[int, int] = {}
    for line in result.stdout.splitlines():
        pid_text, parent_text, kib_text = line.split()
        pid, parent = int(pid_text), int(parent_text)
        rss[pid] = int(kib_text) * 1024
        children.setdefault(parent, []).append(pid)
    if root_pid not in rss:
        raise ResourceLimitError('cannot inspect worker memory')
    pending = [root_pid]
    total = 0
    while pending:
        pid = pending.pop()
        total += rss[pid]
        pending.extend(children.get(pid, ()))
    return total


def _status(path: Path, state: str, reason: str | None = None, **usage: Any) -> dict[str, Any]:
    record = {'state': state, 'reason': reason, **usage}
    temporary = path / 'status.json.tmp'
    temporary.write_text(json.dumps(record, sort_keys=True) + '\n', encoding='utf-8')
    temporary.replace(path / 'status.json')
    return record


def _stop(worker: subprocess.Popen[bytes]) -> None:
    if os.name == 'nt':
        if worker.poll() is None:
            subprocess.run(['taskkill', '/PID', str(worker.pid), '/T', '/F'],
                           capture_output=True, check=False)
    else:
        try:
            os.killpg(worker.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    worker.wait()


def supervise_command(
    command: list[str], output: Path, limits: dict[str, Any], *, poll_seconds: float = 0.1,
    report_name: str = 'experiment.json',
) -> dict[str, Any]:
    """Stop an active worker; atomically publish only a complete experiment.

    Each command argument may use ``{output}`` for the staging directory.
    """
    if report_name not in ('experiment.json', 'preflight.json', 'diagnostic.json'):
        raise ValueError('unsupported supervised report name')
    staging = output.with_name(output.name + '.incomplete')
    if output.exists() or staging.exists():
        raise ValueError('experiment output already exists; refusing overwrite')
    staging.mkdir(parents=True)
    started = time.monotonic()
    peak = 0
    worker = None
    completed = False
    reason = 'worker did not complete'
    try:
        initial = free_disk_bytes(staging)
        if initial < limits['initial_free_disk_bytes_min']:
            raise ResourceLimitError('initial free disk below protocol minimum')
        _require_memory_monitor()
        _status(staging, 'incomplete', 'worker running', initial_free_disk_bytes=initial)
        worker = subprocess.Popen(
            [part.replace('{output}', str(staging)) for part in command],
            start_new_session=(os.name != 'nt'),
            creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0),
        )
        while worker.poll() is None:
            elapsed = time.monotonic() - started
            if free_disk_bytes(staging) < limits['ending_free_disk_bytes_min']:
                raise ResourceLimitError('free disk below protocol reserve')
            try:
                peak = max(peak, process_tree_rss_bytes(worker.pid))
            except ResourceLimitError:
                if worker.poll() is not None:
                    break
                raise
            if peak > limits['peak_working_set_bytes_max']:
                raise ResourceLimitError('memory above protocol ceiling')
            if elapsed > limits['fit_seconds_max_current_phase']:
                raise ResourceLimitError('current phase time above protocol ceiling')
            if elapsed > limits['fit_seconds_max_all']:
                raise ResourceLimitError('all fits time above protocol ceiling')
            progress = staging / 'fit-progress.json'
            if progress.exists():
                marker = json.loads(progress.read_text(encoding='utf-8'))
                if time.monotonic() - marker['started_monotonic'] > limits['fit_seconds_max_each']:
                    raise ResourceLimitError('individual fit time above protocol ceiling')
            time.sleep(poll_seconds)
        if worker.returncode != 0:
            raise ResourceLimitError(f'worker exited with code {worker.returncode}')
        if sys.platform == 'darwin':
            import resource

            # Darwin's ru_maxrss is bytes; this catches a short-lived peak
            # missed by polling for the direct worker process.
            peak = max(peak, resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
        if peak > limits['peak_working_set_bytes_max']:
            raise ResourceLimitError('memory above protocol ceiling')
        if free_disk_bytes(staging) < limits['ending_free_disk_bytes_min']:
            raise ResourceLimitError('ending free disk below protocol reserve')
        if not (staging / report_name).is_file():
            raise ResourceLimitError(f'worker exited without {report_name} report')
        _stop(worker)
        worker = None
        result = _status(staging, 'complete', peak_observed_rss_bytes=peak,
                         elapsed_seconds=round(time.monotonic() - started, 3))
        staging.replace(output)
        completed = True
        return result
    except Exception as error:
        reason = str(error)
        raise
    finally:
        if worker is not None:
            _stop(worker)
        if not completed:
            for name in ('experiment.json', 'preflight.json', 'diagnostic.json',
                         'validation-scores.csv',
                         'test-predictions-sealed.csv'):
                (staging / name).unlink(missing_ok=True)
            shutil.rmtree(staging / 'artifacts', ignore_errors=True)
            _status(staging, 'incomplete', reason, peak_observed_rss_bytes=peak,
                    elapsed_seconds=round(time.monotonic() - started, 3))
