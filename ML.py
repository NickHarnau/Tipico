from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix, multilabel_confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

test = data.copy()

"""
Start der Saison ; Spieltag 1-7 = 0 
Erste Mitte der Saison ; Spieltag 7-17 = 1
Nach WP ; Spieltag 17-21 = 2 
Zweite Mitte der Saison ; Spieltag 21-29 = 3
Endphase d. Saison ; Spieltag 29-34 = 4"""

test.loc[test["Spieltag"] <= 7, "Saisonabschnitt"]=0
test.loc[(test["Spieltag"] <= 17) & (test["Spieltag"] > 7), "Saisonabschnitt"] = 1
test.loc[(test["Spieltag"] <= 21) & (test["Spieltag"] > 17), "Saisonabschnitt"] = 2
test.loc[(test["Spieltag"] <= 29) & (test["Spieltag"] > 21), "Saisonabschnitt"] = 3
test.loc[(test["Spieltag"] <= 34) & (test["Spieltag"] > 29), "Saisonabschnitt"] = 4

# first try predict result


def predict_wins(target_value, state, testsize=0.33):
    Y = test[[target_value]]
    X = test[["Saisonabschnitt", "B365H","B365D","B365A"]]

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=testsize, random_state=state)

    Classifier = [RandomForestClassifier(), LogisticRegression(), LinearSVC(), KNeighborsClassifier(n_neighbors=5), GaussianNB()]
    Predictions = []
    for classifier in Classifier:
        cl = classifier
        cl.fit(X_train, y_train)
        Predictions.append(cl.predict(X_test))
        print(cl.score(X_test, y_test))
        print(classification_report(y_test, cl.predict(X_test)))
        print(confusion_matrix(y_test, cl.predict(X_test)))


    Vorhersage = test.loc[y_test.index]
    Vorhersage["RF"]= Predictions[0]
    Vorhersage["LR"]= Predictions[1]
    Vorhersage["SVC"]= Predictions[2]
    Vorhersage["KNN"]= Predictions[3]
    Vorhersage["GN"]= Predictions[4]

    Columns = ["RF", "LR", "SVC", "KNN", "GN"]

    Gewinne = []

    if target_value == "FTR":
        # predict result
        for column in Columns:
            Gewinn = Vorhersage.loc[Vorhersage["FTR"] == Vorhersage[column]]
            Gewinn.loc[Gewinn["FTR"] == "D", "Gewinn_{}".format(column)] = Gewinn["B365D"]
            Gewinn.loc[Gewinn["FTR"] == "A", "Gewinn_{}".format(column)] = Gewinn["B365A"]
            Gewinn.loc[Gewinn["FTR"] == "H", "Gewinn_{}".format(column)] = Gewinn["B365H"]
            Gewinne.append(Gewinn["Gewinn_{}".format(column)].sum() - len(Vorhersage))
    else:
        # predict favorite win:
        for column in Columns:
            Gewinn = Vorhersage.loc[Vorhersage["favorite_win"] == Vorhersage[column]]
            Gewinn.loc[(Gewinn["difference"] > 0) & (Gewinn["FTR"] == "A"), "Gewinn_{}".format(column)] = Gewinn["B365A"]
            Gewinn.loc[(Gewinn["difference"] < 0) & (Gewinn["FTR"] == "H"), "Gewinn_{}".format(column)] = Gewinn["B365H"]
            Gewinn.loc[(Gewinn["difference"] > 0) & (Gewinn["FTR"] != "A"), "Gewinn_{}".format(column)] = Gewinn["1x"]
            Gewinn.loc[(Gewinn["difference"] < 0) & (Gewinn["FTR"] != "H"), "Gewinn_{}".format(column)] = Gewinn["x2"]
            Gewinne.append(Gewinn["Gewinn_{}".format(column)].sum()-len(Vorhersage))

    dict_wins = dict(zip(Columns, Gewinne))
    return dict_wins


a = predict_wins("FTR", 405)
b = predict_wins("favorite_win", 405)
### nächster versuch : Binär das ganze zu lösen: Gewinnt der Favorit oder nicht?