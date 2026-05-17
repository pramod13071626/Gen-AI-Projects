import numpy as np


def get_feature_importance(model, feature_values, feature_names, disease_type):
    try:
        values = np.array(feature_values).reshape(1, -1)

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            coef = model.coef_[0] if len(model.coef_.shape) > 1 else model.coef_
            importances = np.abs(coef)
        else:
            return None

        total = importances.sum()
        if total == 0:
            return None

        contributions = []
        for i, (name, imp) in enumerate(zip(feature_names, importances)):
            pct = round((imp / total) * 100, 1)
            if pct > 0:
                contributions.append({
                    'feature': name.replace('_', ' ').title(),
                    'value': str(feature_values[i]),
                    'contribution': pct,
                })

        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        return contributions[:8]

    except Exception:
        return None
