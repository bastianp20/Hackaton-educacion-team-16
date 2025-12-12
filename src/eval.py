"""
eval.py - Evaluación y fairness del modelo de riesgo
Hackathon Duoc UC 2025
"""

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, ConfusionMatrixDisplay, brier_score_loss
)
from sklearn.calibration import calibration_curve
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def evaluar_modelo(pipeline, X_test, y_test):
    """Calcula métricas básicas y muestra matriz de confusión."""
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    print(f"Accuracy: {acc:.3f} | Precision: {prec:.3f} | Recall: {rec:.3f} | F1: {f1:.3f}")
    cm = confusion_matrix(y_test, y_pred)
    ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["No Riesgo", "Riesgo"]).plot(cmap="Blues")
    plt.show()

def calibracion(pipeline, X_test, y_test):
    """Calcula el Brier Score y muestra la curva de calibración."""
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    brier = brier_score_loss(y_test, y_proba)
    print(f"📏 Brier Score: {brier:.4f} (menor es mejor)")
    prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=10)
    plt.plot(prob_pred, prob_true, "o-", label="Modelo")
    plt.plot([0,1],[0,1],"--", color="gray", label="Perfecto")
    plt.xlabel("Probabilidad predicha"); plt.ylabel("Probabilidad observada")
    plt.legend(); plt.grid(True); plt.show()

def fairness(pipeline, df_test):
    """Evalúa equidad por género y edad."""
    def evaluar_subgrupos(df, feature):
        resultados = []
        for g in sorted(df[feature].dropna().unique()):
            subset = df[df[feature]==g]
            X = subset[["PROM_GRAL","ASISTENCIA","GEN_ALU","EDAD_ALU"]]
            y = subset["RIESGO"]
            y_pred = pipeline.predict(X)
            resultados.append({
                feature:g,
                "N":len(subset),
                "Accuracy":accuracy_score(y,y_pred),
                "Recall":recall_score(y,y_pred),
                "F1":f1_score(y,y_pred)
            })
        return pd.DataFrame(resultados)

    res_gen = evaluar_subgrupos(df_test,"GEN_ALU")
    df_test["EDAD_GRUPO"] = pd.cut(df_test["EDAD_ALU"],bins=[0,10,14,18,25],
                                   labels=["Niñez","PreAdolescente","Adolescente","Adulto"])
    res_age = evaluar_subgrupos(df_test,"EDAD_GRUPO")

    fig, ax = plt.subplots(1,2,figsize=(10,4))
    sns.barplot(data=res_gen,x="GEN_ALU",y="Recall",ax=ax[0],palette="Blues")
    sns.barplot(data=res_age,x="EDAD_GRUPO",y="Recall",ax=ax[1],palette="Purples")
    ax[0].set_title("Recall por Género"); ax[1].set_title("Recall por Grupo Etario")
    plt.tight_layout(); plt.show()
    return res_gen,res_age
