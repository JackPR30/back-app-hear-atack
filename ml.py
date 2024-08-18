import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import joblib


def entrenar():
    
    datos = pd.read_csv('heart_numeric_no_nans.csv')
    datosX=datos.drop(columns=['HadHeartAttack'])
    
    X_data = datosX
    y_data = datos['HadHeartAttack']

    # Dividir los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

    # Crear y entrenar modelo
    modelo_rf = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo_rf.fit(X_train, y_train)
    predicciones = modelo_rf.predict(X_test)
    joblib.dump(modelo_rf, 'modelo_rf.joblib')
    joblib.dump(X_data, 'X_data.joblib')
    # data.head()

    # y = data["HeartDisease"]
    # X = data.drop(['HeartDisease'],axis=1)
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state = 0)
    # scaler = StandardScaler()
    # X_train = scaler.fit_transform(X_train)
    # X_test = scaler.transform(X_test)

    # m4 = 'Extreme Gradient Boost'
    # xgb = XGBClassifier(learning_rate=0.01, n_estimators=25, max_depth=15,gamma=0.6, subsample=0.52,colsample_bytree=0.6,seed=27,
    #                     reg_lambda=2, booster='dart', colsample_bylevel=0.6, colsample_bynode=0.5)
    # xgb.fit(X_train, y_train)
    # xgb_predicted = xgb.predict(X_test)
    # xgb_conf_matrix = confusion_matrix(y_test, xgb_predicted)
    # xgb_acc_score = accuracy_score(y_test, xgb_predicted)
    # joblib.dump(modelo_rf, 'modelo_rf.joblib')
    # joblib.dump(xgb, 'xgb_model.joblib')
    # print("confussion matrix")
    # print(xgb_conf_matrix)
    # print("\n")
    # print("Accuracy of Extreme Gradient Boost:",xgb_acc_score*100,'\n')
    # print(classification_report(y_test,xgb_predicted))

def preprocess_and_predict(data):
    mensaje = ""
    modelo_rf = joblib.load('modelo_rf.joblib')
    new_prediction = modelo_rf.predict(data)
    
    # Realizar la predicción
    new_prediction = modelo_rf.predict(data)
    predicciones_nuevas = modelo_rf.predict_proba(data)[:, 1]
    mensaje += f"El riesgo estimado de enfermedad cardíaca es de {predicciones_nuevas[0] * 100:.2f}%.\n\n"

    # Calcular impacto de factores
    probabilidad_base = modelo_rf.predict_proba(data)[:, 1]
    X = joblib.load('X_data.joblib')
    impactos = {}
    
    for feature in X.columns:
        temp_df = data.copy()
        valor_original = temp_df[feature].values[0]
        valor_medio = X[feature].mean()
        temp_df[feature] = valor_medio
        probabilidad_cambiada = modelo_rf.predict_proba(temp_df)[:, 1]
        impacto = abs(probabilidad_cambiada - probabilidad_base)[0]
        impactos[feature] = impacto
    
    impacto_df = pd.DataFrame(list(impactos.items()), columns=['Feature', 'Impact'])
    impacto_df = impacto_df.sort_values(by='Impact', ascending=False)
    
    # Construir la cadena de impacto de factores con saltos de línea adecuados
    importancias = []
    for index, row in impacto_df.iterrows():
        importancias.append(f"- {row['Feature']}: {row['Impact']:.2f}")

    # Unir la lista de importancias en un string con saltos de línea
    mensaje_importancias = "\n".join(importancias)
    mensaje_importancias_text = str(mensaje_importancias)

    # Construir el mensaje final
    mensaje += f"Las características más influyentes en la predicción son:\n\n{mensaje_importancias}\n\nPor lo tanto, según el modelo:\n"
    mensaje += "Presentas una enfermedad cardíaca" if new_prediction[0] == 1 else "No presentas una enfermedad cardíaca"
    
    return mensaje,impacto_df,new_prediction[0],predicciones_nuevas[0], mensaje_importancias_text

entrenar()
