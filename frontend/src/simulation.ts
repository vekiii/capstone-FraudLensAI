// T007 import boundary only. Client/decoder/view behavior belongs to T010.
export interface SimulationClient {
  listScenarios(options?: { signal?: AbortSignal }): Promise<unknown>;
  compare(recipe: unknown, options?: { signal?: AbortSignal }): Promise<unknown>;
}

export function mountSimulation(_root: HTMLElement, _client: SimulationClient): () => void {
  return () => {};
}
