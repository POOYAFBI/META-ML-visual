# Model Comparison Dashboard Data Contract

This document defines the frontend data contract for the **Model Performance Comparison** dashboard (`مقایسه عملکرد مدل‌ها`). It is shared by the frontend and backend: the comparison API must return this shape so the dashboard can consume real evaluation data without UI changes.

The frontend mock data in `frontend/app.js` uses this exact structure under `mockComparisonData.regression` and `mockComparisonData.classification`, and the backend returns the same shape from `/api/comparison`.

## Endpoint intent

The backend exposes one response per task:

```http
GET /api/comparison?task=regression
GET /api/comparison?task=classification
```

The response body is one JSON object matching the schema below.

## Top-level JSON shape

```json
{
  "task": "regression | classification",
  "primary_metric": "rmse | weighted_f1 | ...",
  "primary_metric_direction": "lower | higher",
  "rows": [],
  "summary_cards": [],
  "best": {},
  "insights": {},
  "metric_definitions": {},
  "chart_config": []
}
```

### Top-level fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `task` | string | yes | Task represented by the payload. Allowed values are `regression` and `classification`. |
| `primary_metric` | string | yes | Metric key used for primary ranking and headline summary, for example `rmse` or `weighted_f1`. |
| `primary_metric_direction` | string | yes | Whether the primary metric is better when `lower` or `higher`. |
| `rows` | array | yes | Table/chart rows. Each row is one dataset/model pair. |
| `summary_cards` | array | yes | Ordered summary cards shown at the top of the dashboard. |
| `best` | object | yes | Best-row metadata used for highlighting and comparison text. |
| `insights` | object | yes | Copy for the insight panel. |
| `metric_definitions` | object | yes | Display label, direction, and helper text for every metric used by the payload. |
| `chart_config` | array | yes | Ordered chart definitions. The current UI expects two charts per task. |

## Row contract: regression

Regression rows must include the following fields.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | yes | Stable unique row id. Used by table selection, chart bar selection, and `best.row_id`. |
| `dataset_id` | string | yes | Dataset id used by the app, for example `A` or `B`. |
| `dataset_label_fa` | string | yes | Persian human-readable dataset label. Displayed first. |
| `dataset_label_en` | string | yes | English dataset label. Displayed in parentheses or muted subtext. |
| `dataset_raw_name` | string | yes | Raw backend/training dataset name. Must remain available for details/tooltips. |
| `model_label_fa` | string | yes | Persian human-readable model label. Displayed first. |
| `model_label_en` | string | yes | English model label. Displayed in parentheses or muted subtext. |
| `model_raw_name` | string | yes | Raw backend/training model name. Must remain available for details/tooltips. |
| `rmse` | number | yes | Root Mean Squared Error. Lower is better. |
| `mae` | number | yes | Mean Absolute Error. Lower is better. |
| `r2` | number | yes | R² score. Higher is better. |
| `normalized_rmse` | number | yes | RMSE normalized to a comparable scale. Lower is better. |
| `rank` | number | yes | 1-based rank. `1` should correspond to `best.row_id`. |
| `interpretation` | string | yes | Short bilingual-ready human interpretation for detail panel and summary use. |

## Row contract: classification

Classification rows must include the following fields.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | yes | Stable unique row id. Used by table selection, chart bar selection, and `best.row_id`. |
| `dataset_id` | string | yes | Dataset id used by the app, for example `A`, `B`, or `C`. |
| `dataset_label_fa` | string | yes | Persian human-readable dataset label. Displayed first. |
| `dataset_label_en` | string | yes | English dataset label. Displayed in parentheses or muted subtext. |
| `dataset_raw_name` | string | yes | Raw backend/training dataset name. Must remain available for details/tooltips. |
| `model_label_fa` | string | yes | Persian human-readable model label. Displayed first. |
| `model_label_en` | string | yes | English model label. Displayed in parentheses or muted subtext. |
| `model_raw_name` | string | yes | Raw backend/training model name. Must remain available for details/tooltips. |
| `accuracy` | number | yes | Accuracy score. Higher is better. |
| `weighted_f1` | number | yes | Weighted F1 score. Higher is better. |
| `macro_f1` | number | yes | Macro F1 score. Higher is better. |
| `rank` | number | yes | 1-based rank. `1` should correspond to `best.row_id`. |
| `interpretation` | string | yes | Short bilingual-ready human interpretation for detail panel and summary use. |

## Summary card contract

`summary_cards` is an ordered array. The frontend renders cards in this order.

```json
{
  "id": "best_model",
  "title": "Best model",
  "value": "جنگل تصادفی (Random Forest)",
  "detail": "random_forest"
}
```

Required summary card fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | yes | Stable card id. Recommended values: `best_model`, `best_pair`, `primary_metric`, `key_takeaway`. |
| `title` | string | yes | Short English title currently displayed in the card header. |
| `value` | string | yes | Main card value. Persian label should appear first when referring to model/dataset names. |
| `detail` | string | yes | Muted technical detail, raw name, or metric direction. |

## Best-row contract

```json
{
  "row_id": "reg-a-rf",
  "rank": 1,
  "primary_metric_value": 27450
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `row_id` | string | yes | Must match one `rows[].id`. This row receives best-row highlighting. |
| `rank` | number | yes | Expected to be `1` for the best row. |
| `primary_metric_value` | number | yes | Value of `primary_metric` for the best row. |

## Insights contract

```json
{
  "overall_takeaway": "...",
  "dataset_effect": "...",
  "model_behavior": "...",
  "metric_caution": "..."
}
```

The frontend displays all four fields as separate insight cards:

- `overall_takeaway`
- `dataset_effect`
- `model_behavior`
- `metric_caution`

## Metric definitions and direction rules

Every metric rendered in the table or charts must have a definition in `metric_definitions`.

```json
{
  "rmse": {
    "label": "RMSE",
    "direction": "lower",
    "helper_text": "RMSE: lower is better"
  }
}
```

Required metric definition fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `label` | string | yes | Display label for table/chart/tooltips. |
| `direction` | string | yes | `lower` or `higher`. Used for best metric highlighting. |
| `helper_text` | string | yes | Helper text shown near charts. |

Metric direction rules are fixed:

| Metric key | Display label | Direction |
| --- | --- | --- |
| `rmse` | RMSE | lower is better |
| `mae` | MAE | lower is better |
| `normalized_rmse` | Normalized RMSE | lower is better |
| `r2` | R² | higher is better |
| `accuracy` | Accuracy | higher is better |
| `weighted_f1` | Weighted F1 | higher is better |
| `macro_f1` | Macro F1 | higher is better |

## Chart config contract

The current dashboard expects two chart configs per task.

```json
{
  "id": "rmse_by_pair",
  "title": "RMSE by model/dataset",
  "metric": "rmse"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | string | yes | Stable chart id for analytics/tests/future API evolution. |
| `title` | string | yes | Chart title. |
| `metric` | string | yes | Metric key from each row and from `metric_definitions`. |

Current chart mapping:

- Regression chart 1: `rmse`
- Regression chart 2: `r2`
- Classification chart 1: `accuracy`
- Classification chart 2: `weighted_f1`

## Display rules

1. Persian human-readable labels must be shown first.
2. English labels or technical names must remain visible in parentheses or muted subtext.
3. Raw names (`dataset_raw_name`, `model_raw_name`) must remain available for tooltips, detail panels, QA, and debugging.
4. Do not remove `dataset_id`; it is distinct from `dataset_raw_name` and helps connect the comparison row to app selections.
5. Long bilingual labels must be treated as wrappable UI text.

## Frontend behavior rules

### Best row selection

- The best row is selected from `best.row_id`.
- `best.row_id` must match exactly one `rows[].id`.
- The best row receives visual highlighting in the table and chart border styling.
- `rank: 1` should correspond to `best.row_id`; if it does not, the payload should be considered invalid.

### Best metric highlighting

- For each rendered metric column, the frontend reads `metric_definitions[metric].direction`.
- If direction is `lower`, the minimum value in that metric column is highlighted.
- If direction is `higher`, the maximum value in that metric column is highlighted.

### Chart bars map to rows

- Chart labels are generated from each row as: `dataset_label_fa (dataset_label_en) / model_label_fa (model_label_en)`.
- Chart data values are generated from the row metric named by `chart_config[].metric`.
- Chart bar index maps directly to `rows[index]`.
- Clicking a chart bar selects `rows[index].id`.

### Selected row updates detail panel

- The selected row is tracked by row `id`.
- Clicking a table row or chart bar updates the selected id.
- The detail panel displays labels, raw names, rank, task metrics, interpretation, and comparison against the best row.

### Insights display

- Each field in `insights` renders as one card.
- Insight copy is task-specific and should be safe to display directly.

## Full example JSON: regression

```json
{
  "task": "regression",
  "primary_metric": "rmse",
  "primary_metric_direction": "lower",
  "rows": [
    {
      "id": "reg-a-rf",
      "dataset_id": "A",
      "dataset_label_fa": "دیتاست A — پایه",
      "dataset_label_en": "Dataset A / Baseline Housing",
      "dataset_raw_name": "baseline_dataset",
      "model_label_fa": "جنگل تصادفی",
      "model_label_en": "Random Forest",
      "model_raw_name": "random_forest",
      "rmse": 27450,
      "mae": 18220,
      "r2": 0.89,
      "normalized_rmse": 0.118,
      "rank": 1,
      "interpretation": "بهترین تعادل خطا و توضیح‌پذیری؛ روی داده پایه پایدارترین رفتار را دارد."
    },
    {
      "id": "reg-b-xgb",
      "dataset_id": "B",
      "dataset_label_fa": "دیتاست B — ویژگی‌سازی‌شده",
      "dataset_label_en": "Dataset B / Enhanced Features",
      "dataset_raw_name": "enhanced_dataset",
      "model_label_fa": "ایکس‌جی‌بوست",
      "model_label_en": "XGBoost",
      "model_raw_name": "xgboost",
      "rmse": 28680,
      "mae": 19040,
      "r2": 0.875,
      "normalized_rmse": 0.123,
      "rank": 2,
      "interpretation": "با ویژگی‌های بیشتر بهتر از مدل خطی عمل می‌کند اما کمی واریانس خطا دارد."
    }
  ],
  "summary_cards": [
    {
      "id": "best_model",
      "title": "Best model",
      "value": "جنگل تصادفی (Random Forest)",
      "detail": "random_forest"
    },
    {
      "id": "best_pair",
      "title": "Best dataset/model pair",
      "value": "دیتاست A — پایه (Dataset A / Baseline Housing) / جنگل تصادفی (Random Forest)",
      "detail": "baseline_dataset / random_forest"
    },
    {
      "id": "primary_metric",
      "title": "Primary metric",
      "value": "RMSE",
      "detail": "lower is better"
    },
    {
      "id": "key_takeaway",
      "title": "Key takeaway",
      "value": "بهترین تعادل خطا و توضیح‌پذیری؛ روی داده پایه پایدارترین رفتار را دارد.",
      "detail": "Mock data only — ready for future API shape"
    }
  ],
  "best": {
    "row_id": "reg-a-rf",
    "rank": 1,
    "primary_metric_value": 27450
  },
  "insights": {
    "overall_takeaway": "در داده mock، مدل‌های درختی خطای قیمت را کمتر از مدل خطی نگه می‌دارند.",
    "dataset_effect": "تغییر دیتاست همیشه بهبود ایجاد نمی‌کند؛ Normalized RMSE کمک می‌کند اثر مقیاس قیمت کنترل شود.",
    "model_behavior": "Random Forest پایدار است؛ XGBoost حساس‌تر ولی رقابتی است؛ Linear Regression خط مبنای قابل توضیح می‌دهد.",
    "metric_caution": "RMSE به خطاهای بزرگ حساس است؛ MAE و R² را همزمان بخوانید."
  },
  "metric_definitions": {
    "rmse": {"label": "RMSE", "direction": "lower", "helper_text": "RMSE: lower is better"},
    "mae": {"label": "MAE", "direction": "lower", "helper_text": "MAE: lower is better"},
    "r2": {"label": "R²", "direction": "higher", "helper_text": "R²: higher is better"},
    "normalized_rmse": {"label": "Normalized RMSE", "direction": "lower", "helper_text": "normalized RMSE: lower is better"}
  },
  "chart_config": [
    {"id": "rmse_by_pair", "title": "RMSE by model/dataset", "metric": "rmse"},
    {"id": "r2_by_pair", "title": "R² by model/dataset", "metric": "r2"}
  ]
}
```

## Full example JSON: classification

```json
{
  "task": "classification",
  "primary_metric": "weighted_f1",
  "primary_metric_direction": "higher",
  "rows": [
    {
      "id": "cls-c-xgb",
      "dataset_id": "C",
      "dataset_label_fa": "دیتاست C — ویژگی‌سازی طبقه‌بندی",
      "dataset_label_en": "Dataset C / Classification Features",
      "dataset_raw_name": "enhanced_dataset",
      "model_label_fa": "ایکس‌جی‌بوست",
      "model_label_en": "XGBoost",
      "model_raw_name": "xgboost",
      "accuracy": 0.884,
      "weighted_f1": 0.879,
      "macro_f1": 0.842,
      "rank": 1,
      "interpretation": "بهترین عملکرد کلی؛ کلاس‌های پرتعداد و کم‌تعداد را نسبتاً متوازن مدیریت می‌کند."
    },
    {
      "id": "cls-c-rf",
      "dataset_id": "C",
      "dataset_label_fa": "دیتاست C — ویژگی‌سازی طبقه‌بندی",
      "dataset_label_en": "Dataset C / Classification Features",
      "dataset_raw_name": "enhanced_dataset",
      "model_label_fa": "جنگل تصادفی",
      "model_label_en": "Random Forest",
      "model_raw_name": "random_forest",
      "accuracy": 0.861,
      "weighted_f1": 0.854,
      "macro_f1": 0.811,
      "rank": 2,
      "interpretation": "دقت خوب دارد اما برای کلاس‌های کوچک‌تر کمی افت Macro F1 دیده می‌شود."
    }
  ],
  "summary_cards": [
    {
      "id": "best_model",
      "title": "Best model",
      "value": "ایکس‌جی‌بوست (XGBoost)",
      "detail": "xgboost"
    },
    {
      "id": "best_pair",
      "title": "Best dataset/model pair",
      "value": "دیتاست C — ویژگی‌سازی طبقه‌بندی (Dataset C / Classification Features) / ایکس‌جی‌بوست (XGBoost)",
      "detail": "enhanced_dataset / xgboost"
    },
    {
      "id": "primary_metric",
      "title": "Primary metric",
      "value": "Weighted F1",
      "detail": "higher is better"
    },
    {
      "id": "key_takeaway",
      "title": "Key takeaway",
      "value": "بهترین عملکرد کلی؛ کلاس‌های پرتعداد و کم‌تعداد را نسبتاً متوازن مدیریت می‌کند.",
      "detail": "Mock data only — ready for future API shape"
    }
  ],
  "best": {
    "row_id": "cls-c-xgb",
    "rank": 1,
    "primary_metric_value": 0.879
  },
  "insights": {
    "overall_takeaway": "در داده mock، XGBoost بهترین Weighted F1 را دارد و تعادل کلاس‌ها بهتر حفظ شده است.",
    "dataset_effect": "ویژگی‌سازی طبقه‌بندی برای مدل‌های غیرخطی مفیدتر از مدل لجستیک ساده است.",
    "model_behavior": "مدل‌های غیرخطی مرزهای تصمیم پیچیده‌تر را بهتر می‌گیرند اما باید با Macro F1 کنترل شوند.",
    "metric_caution": "Accuracy در کلاس‌های نامتوازن کافی نیست؛ Weighted F1 و Macro F1 را کنار آن ببینید."
  },
  "metric_definitions": {
    "accuracy": {"label": "Accuracy", "direction": "higher", "helper_text": "Accuracy: higher is better"},
    "weighted_f1": {"label": "Weighted F1", "direction": "higher", "helper_text": "Weighted F1: higher is better"},
    "macro_f1": {"label": "Macro F1", "direction": "higher", "helper_text": "Macro F1: higher is better"}
  },
  "chart_config": [
    {"id": "accuracy_by_pair", "title": "Accuracy by model/dataset", "metric": "accuracy"},
    {"id": "weighted_f1_by_pair", "title": "Weighted F1 by model/dataset", "metric": "weighted_f1"}
  ]
}
```
