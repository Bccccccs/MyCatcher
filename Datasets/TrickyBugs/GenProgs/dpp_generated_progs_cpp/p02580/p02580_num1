#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int H, W, M;
    cin >> H >> W >> M;
    
    vector<int> rowCount(H + 1, 0);
    vector<int> colCount(W + 1, 0);
    set<pair<int, int>> bombs;
    
    for (int i = 0; i < M; ++i) {
        int h, w;
        cin >> h >> w;
        rowCount[h]++;
        colCount[w]++;
        bombs.insert({h, w});
    }
    
    int maxRow = *max_element(rowCount.begin(), rowCount.end());
    int maxCol = *max_element(colCount.begin(), colCount.end());
    
    vector<int> maxRows, maxCols;
    for (int i = 1; i <= H; ++i) {
        if (rowCount[i] == maxRow) maxRows.push_back(i);
    }
    for (int j = 1; j <= W; ++j) {
        if (colCount[j] == maxCol) maxCols.push_back(j);
    }
    
    int ans = maxRow + maxCol - 1;
    
    if ((long long)maxRows.size() * maxCols.size() > M) {
        ans = maxRow + maxCol;
    } else {
        bool found = false;
        for (int r : maxRows) {
            for (int c : maxCols) {
                if (bombs.find({r, c}) == bombs.end()) {
                    found = true;
                    break;
                }
            }
            if (found) break;
        }
        if (found) ans = maxRow + maxCol;
    }
    
    cout << ans << "\n";
    
    return 0;
}
