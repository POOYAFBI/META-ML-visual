const $ = id => document.getElementById(id);
let charts = {}, currentFeatures = [], currentPresets = [], currentSamples = [], vizState = null, lastPrediction = null;
let decisionSurfaceState = {data:null, loading:false, error:null, selectedPoint:null};
const modelDisplay = {
  linear_regression: {labelFa: 'رگرسیون خطی', labelEn: 'Linear Regression', raw: 'linear_regression', short: 'Linear'},
  logistic_regression: {labelFa: 'رگرسیون لجستیک', labelEn: 'Logistic Regression', raw: 'logistic_regression', short: 'Logistic'},
  random_forest: {labelFa: 'جنگل تصادفی', labelEn: 'Random Forest', raw: 'random_forest', short: 'RF'},
  xgboost: {labelFa: 'ایکس‌جی‌بوست', labelEn: 'XGBoost', raw: 'xgboost', short: 'XGBoost'}
};
const faModel = modelDisplay;
const datasetDisplay = {
  baseline_dataset: {labelFa: 'دیتاست پایه', labelEn: 'baseline_dataset', raw: 'baseline_dataset', short: 'Baseline'},
  enhanced_dataset: {labelFa: 'دیتاست ویژگی‌سازی‌شده', labelEn: 'enhanced_dataset', raw: 'enhanced_dataset', short: 'Enhanced'},
  A: {labelFa: 'دیتاست A — پایه', labelEn: 'Dataset A / baseline_dataset', raw: 'A', short: 'A'},
  B: {labelFa: 'دیتاست B — ویژگی‌سازی حداقلی', labelEn: 'Dataset B / enhanced_dataset', raw: 'B', short: 'B'},
  C: {labelFa: 'دیتاست C — ویژگی‌سازی طبقه‌بندی', labelEn: 'Dataset C / enhanced_dataset', raw: 'C', short: 'C'}
};
const featureDisplay = {
  OverallQual: {labelFa: 'کیفیت کلی ساختمان', labelEn: 'OverallQual', raw: 'OverallQual', short: 'OverallQual'},
  GrLivArea: {labelFa: 'زیربنای قابل سکونت', labelEn: 'GrLivArea', raw: 'GrLivArea', short: 'GrLivArea'},
  Neighborhood: {labelFa: 'محله', labelEn: 'Neighborhood', raw: 'Neighborhood', short: 'Neighborhood'}
};
const faTask = {regression:'رگرسیون', classification:'طبقه‌بندی'};
const faDataset = Object.fromEntries(Object.entries(datasetDisplay).map(([k, v]) => [k, `${v.labelFa} (${v.labelEn})`]));
const reliabilityFa = {high:'بالا', medium:'متوسط', low:'پایین'};
const severityFa = {low:'کم', medium:'متوسط', high:'زیاد'};
