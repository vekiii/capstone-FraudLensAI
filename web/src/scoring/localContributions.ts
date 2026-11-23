/** Separate experimental wire decoder; published v2 case contracts stay closed. */
export interface LocalContribution {
  contract_version: 1;
  status: 'available';
  method: 'lightgbm_pred_contrib_log_odds_v1';
  explained_scale: 'log_odds';
  case_id: string;
  transaction_id: string;
  assessment_run_id: string;
  feature_snapshot_digest: string;
  evidence_digest: string;
  base_value: number;
  raw_score: number;
  score: number;
  remainder: number;
  items: { feature_key: string; observed_value: string; unit: string;
    direction: 'increases' | 'decreases' | 'neutral'; contribution: number }[];
}

export type LocalContributionResponse = LocalContribution |
  { contract_version: 1; status: 'unavailable' | 'invalid'; reason_code: string };

const record = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value);
const finite = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);
const availableKeys = ['assessment_run_id', 'base_value', 'canonical_transaction_id', 'case_id',
  'context_revision', 'contract_version', 'dataset_version', 'evidence_digest', 'explained_scale',
  'feature_snapshot_digest', 'feature_version', 'items', 'manifest_sha256', 'matrix_feature_order_sha256',
  'method', 'model_sha256', 'num_iteration', 'objective', 'partial', 'raw_score', 'remainder',
  'score', 'status', 'transaction_id'];

export function decodeLocalContribution(value: unknown): LocalContributionResponse {
  if (!record(value) || value.contract_version !== 1) throw new Error('Invalid local contribution response');
  if (value.status === 'unavailable' || value.status === 'invalid') {
    if (typeof value.reason_code !== 'string' || Object.keys(value).sort().join(',') !==
        'contract_version,reason_code,status') throw new Error('Invalid local contribution response');
    return value as LocalContributionResponse;
  }
  if (value.status !== 'available' || value.method !== 'lightgbm_pred_contrib_log_odds_v1' ||
      value.explained_scale !== 'log_odds' || value.objective !== 'binary sigmoid:1' ||
      value.num_iteration !== 140 || value.partial !== true ||
      Object.keys(value).sort().join(',') !== availableKeys.sort().join(',') ||
      !Array.isArray(value.items) || value.items.length !== 3 ||
      ![value.score, value.raw_score, value.base_value, value.remainder].every(finite) ||
      !['case_id', 'transaction_id', 'assessment_run_id', 'feature_snapshot_digest', 'evidence_digest']
        .every(key => typeof value[key] === 'string') ||
      !['model_sha256', 'manifest_sha256', 'matrix_feature_order_sha256', 'context_revision']
        .every(key => typeof value[key] === 'string' && /^[0-9a-f]{64}$/.test(value[key])) ||
      !value.items.every(item => record(item) && typeof item.feature_key === 'string' &&
        typeof item.observed_value === 'string' && typeof item.unit === 'string' &&
        Object.keys(item).sort().join(',') === 'contribution,direction,feature_key,observed_value,unit' &&
        ['increases', 'decreases', 'neutral'].includes(String(item.direction)) && finite(item.contribution) &&
        item.direction === (item.contribution > 0 ? 'increases' : item.contribution < 0 ? 'decreases' : 'neutral')) ||
      (value.score as number) < 0 || (value.score as number) > 1) {
    throw new Error('Invalid local contribution response');
  }
  const terms = value.items.map(item => item.contribution as number);
  if (Math.abs((value.base_value as number) + terms.reduce((a, b) => a + b, 0) +
      (value.remainder as number) - (value.raw_score as number)) > 1e-8) {
    throw new Error('Invalid local contribution response');
  }
  const raw = value.raw_score as number;
  const score = raw >= 0 ? 1 / (1 + Math.exp(-raw)) : Math.exp(raw) / (1 + Math.exp(raw));
  if (Math.abs(score - (value.score as number)) > 1e-12) throw new Error('Invalid local contribution response');
  return value as unknown as LocalContribution;
}
