from data_cleaning import clean_data
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_graph(df, att):
    sns.stripplot(x='move', y=att, data=df, jitter=True);
    plt.show()

def main():
    my_filename = "raw_accel.csv"
    moves = pd.DataFrame(clean_data(my_filename, None, None))
    X = moves[moves.columns[2:]]
    y = moves['move']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    neighbours = 15
    knn_model = KNeighborsClassifier(n_neighbors=neighbours)
    nb_model = GaussianNB()
    knn_model.fit(X_train, y_train)
    nb_model.fit(X_train, y_train)
    my_knn_score = knn_model.score(X_test, y_test)
    my_nb_score = nb_model.score(X_test, y_test)
    
    a_filename = "subject_a.csv"
    a_moves = pd.DataFrame(clean_data(a_filename, None, None))
    X_a = a_moves[a_moves.columns[2:]]
    y_a = a_moves['move']
    a_score = knn_model.score(X_a, y_a)
    
    b_filename = "subject_b.csv"
    b_moves = pd.DataFrame(clean_data(b_filename, None, None))
    X_b = b_moves[b_moves.columns[2:]]
    y_b = b_moves['move']
    b_score = knn_model.score(X_b, y_b)
    
    c_filename = "subject_d.csv"
    c_moves = pd.DataFrame(clean_data(d_filename, None, None))
    X_d = d_moves[d_moves.columns[2:]]
    y_d = d_moves['move']
    c_score = knn_model.score(X_d, y_d)
    
    c_filename = "subject_c.csv"
    c_moves = pd.DataFrame(clean_data(c_filename, None, None))
    X_c = c_moves[c_moves.columns[2:]]
    y_c = c_moves['move']
    c_score = knn_model.score(X_c, y_c)

    others = pd.concat([a_moves, b_moves, c_moves, d_moves])

    others_score = knn_model.score(others[others.columns[2:]], others['move'])

    
if __name__ == '__main__':
    main()
