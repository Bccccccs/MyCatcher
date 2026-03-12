#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <unordered_map>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int H, W, M;
    cin >> H >> W >> M;

    vector<int> rowCount(H + 1, 0);
    vector<int> colCount(W + 1, 0);
    map<pair<int, int>, bool> bombMap;

    for (int i = 0; i < M; ++i) {
        int h, w;
        cin >> h >> w;
        rowCount[h]++;
        colCount[w]++;
        bombMap[{h, w}] = true;
    }

    int maxRow = 0;
    for (int i = 1; i <= H; ++i) {
        if (rowCount[i] > maxRow) {
            maxRow = rowCount[i];
        }
    }
    vector<int> maxRows;
    for (int i = 1; i <= H; ++i) {
        if (rowCount[i] == maxRow) {
            maxRows.push_back(i);
        }
    }

    int maxCol = 0;
    for (int i = 1; i <= W; ++i) {
        if (colCount[i] > maxCol) {
            maxCol = colCount[i];
        }
    }
    vector<int> maxCols;
    for (int i = 1; i <= W; ++i) {
        if (colCount[i] == maxCol) {
            maxCols.push_back(i);
        }
    }

    long long totalPairs = (long long)maxRows.size() * maxCols.size();
    if (totalPairs > M) {
        cout << maxRow + maxCol << "\n";
        return 0;
    }

    for (int r : maxRows) {
        for (int c : maxCols) {
            if (bombMap.find({r, c}) == bombMap.end()) {
                cout << maxRow + maxCol << "\n";
                return 0;
            }
        }
    }

    cout << maxRow + maxCol - 1 << "\n";
    return 0;
}
