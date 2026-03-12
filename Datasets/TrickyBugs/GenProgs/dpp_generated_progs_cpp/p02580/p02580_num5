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
    map<pair<int, int>, bool> bombs;

    for (int i = 0; i < M; ++i) {
        int h, w;
        cin >> h >> w;
        rowCount[h]++;
        colCount[w]++;
        bombs[{h, w}] = true;
    }

    int maxRow = 0;
    for (int i = 1; i <= H; ++i) {
        maxRow = max(maxRow, rowCount[i]);
    }
    vector<int> maxRows;
    for (int i = 1; i <= H; ++i) {
        if (rowCount[i] == maxRow) {
            maxRows.push_back(i);
        }
    }

    int maxCol = 0;
    for (int i = 1; i <= W; ++i) {
        maxCol = max(maxCol, colCount[i]);
    }
    vector<int> maxCols;
    for (int i = 1; i <= W; ++i) {
        if (colCount[i] == maxCol) {
            maxCols.push_back(i);
        }
    }

    int ans = maxRow + maxCol - 1;
    bool foundBetter = false;

    for (int r : maxRows) {
        for (int c : maxCols) {
            if (bombs.find({r, c}) == bombs.end()) {
                ans = maxRow + maxCol;
                foundBetter = true;
                break;
            }
        }
        if (foundBetter) break;
    }

    cout << ans << "\n";
    return 0;
}
