import pandas as pd


def retrive(result, data, text):
    for index, col in enumerate(data):
        if not isinstance(col, str):
            continue
        col = col.lower().replace('\n', '').replace('\r', '')

        searchStrings = text.split()
        for searchText in searchStrings:
            if searchText not in col:
                break
        else:
            pos = col.find(searchText)
            colSubstring = col[pos - 50: pos + 90]
            result[index] = [col, colSubstring]
    return result


def remove(result, text):
    for index in list(result.keys()):
        if text in result[index][0]:
            del result[index]


def main():
    RSU = '/Users/q115346/PycharmProjects/MountWizzard4/RSU-Cases-2020-11-12.csv'
    NAV = '/Users/q115346/PycharmProjects/MountWizzard4/Navi-Cases-2020-11-12.csv'

    df = pd.read_csv(NAV, delimiter=';')
    data = df['Beschreibung']

    keywords = ['ziel nicht', 'adress nicht', 'favo', 'komfort', 'ziel kein']
    negKeywords = ['e-mail-a', 'e-mail adresse', 'email-adresse', 'favoritentaste']

    result = dict()
    for keyword in keywords:
        result = retrive(result, data, keyword)
    for keyword in negKeywords:
        remove(result, keyword)

    print(len(result), len(data))
    for index, text in result.items():
        print(index, text[1])


if __name__ == "__main__":
    main()
