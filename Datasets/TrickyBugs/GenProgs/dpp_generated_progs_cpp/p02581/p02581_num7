#include <iostream>
#include <vector>
#include <algorithm>
#include <cstring>
using namespace std;

const int MAXN = 2005;
int dp[MAXN][MAXN];
int pos[MAXN][3];
int seq[MAXN * 3];

int main() {
    int N;
    cin >> N;
    int M = 3 * N;
    for (int i = 0; i < M; ++i) {
        cin >> seq[i];
    }

    vector<int> cnt(N + 1, 0);
    for (int v = 1; v <= N; ++v) {
        pos[v][0] = pos[v][1] = pos[v][2] = -1;
    }
    for (int i = 0; i < M; ++i) {
        int v = seq[i];
        pos[v][cnt[v]++] = i;
    }

    memset(dp, -1, sizeof(dp));
    dp[0][M] = 0;

    for (int l = 0; l <= M; ++l) {
        for (int r = M; r >= l; --r) {
            if (dp[l][r] == -1) continue;
            int len = r - l;
            if (len == 0) continue;

            // take i-th from left and i-th from right
            // i ranges from 1 to len
            // but we can think of taking from both ends
            // but here the rule is symmetric removal by index from both sides
            // Let's think differently:
            // We process by removing pairs (l + i - 1, r - i)
            // where i from 1 to len/2
            // But we need DP over intervals.

            // Better: DP[l][r] = max score in interval [l, r)
            // We can remove a pair (l + k, r - 1 - k) for k = 0..(len/2 - 1)
            // Wait, the rule: choose index i, remove i-th from left in current array
            // and i-th from right in current array.
            // This means if current array is A[l..r-1], then we remove A[l + i - 1] and A[r - i].
            // After removal, the remaining array is A[l..l+i-2] concatenated with A[l+i..r-i-1] concatenated with A[r-i+1..r-1].
            // This splits into two independent segments: left segment [l, l+i-1) and right segment [r-i, r-1) are removed,
            // middle segment [l+i, r-i-1] remains.
            // Actually careful: removing i-th from left (index L = l + i - 1) and i-th from right (index R = r - i).
            // After removal, the remaining cards are indices [l, L-1] and [L+1, R-1] and [R+1, r-1].
            // But note [l, L-1] and [R+1, r-1] are adjacent in the new array? No, they become separate segments.
            // Actually the new array is: first i-1 cards from left, then cards between L and R (excluding L and R),
            // then last i-1 cards from right. So it's three segments concatenated.
            // This is messy for DP.

            // Known trick: This problem is equivalent to: we can remove two cards at symmetric positions
            // if they have same value, get +1, and also we can remove any card individually without scoring?
            // Actually no, we must remove two cards each time, one from left i-th and one from right i-th.
            // This is equivalent to: we can pair cards that are symmetric in the current sequence.
            // This is similar to removing matching parentheses in a symmetric way.

            // Alternative viewpoint: Let’s define DP[l][r] = max score for subarray [l, r) (r exclusive).
            // Operation: choose i (1 <= i <= (r-l)/2), remove l + i - 1 and r - i.
            // Then remaining is [l, l+i-1) and [l+i, r-i) and [r-i+1, r). Wait, check:
            // Removing indices p = l + i - 1 and q = r - i.
            // The remaining array is: [l, p), [p+1, q), [q+1, r).
            // But these three segments are contiguous in the new array? The new array is:
            // first i-1 cards: [l, p)
            // then cards between p and q: [p+1, q)
            // then last i-1 cards: [q+1, r)
            // So new array = [l, p) + [p+1, q) + [q+1, r).
            // So it's like we split into three independent segments: [l, p), [p+1, q), [q+1, r).
            // But note lengths: first segment length i-1, last segment length i-1, middle segment length (q - p - 1) = (r - i) - (l + i - 1) - 1 = r - l - 2i.
            // So DP[l][r] = max over i of (score for pair (p,q) + DP[l][p] + DP[p+1][q] + DP[q+1][r]).
            // But DP[l][p] is for segment [l, p) which is length i-1, similarly last segment.
            // However, we can't just add DP because after removal the three segments become separate games? Actually they are concatenated, so further moves can take cards across segment boundaries? Wait, after removal, the array is concatenated, so boundaries disappear. So we cannot treat them independently. So that approach fails.

            // Let's think differently: This is equivalent to: we can remove pairs of cards that are symmetric with respect to the center of the current sequence. This is similar to "removing matched pairs in a palindrome".
            // Known solution: DP[l][r] = max score for subsequence from l to r inclusive.
            // We consider removing the outermost pair: choose i=1, remove l and r.
            // Then remaining is [l+1, r-1].
            // So DP[l][r] = max(DP[l+1][r-1] + (seq[l]==seq[r]), DP[l][r]).
            // Also, we can split at some k: DP[l][r] = max(DP[l][k] + DP[k+1][r]).
            // But does splitting make sense? Because operation always removes symmetric positions, not arbitrary inner pairs.
            // Actually, if we think of the process as: at each step, we remove two cards that are symmetric in the current sequence. This is exactly like removing matched pairs in a string where we can only remove characters at symmetric positions. This is known as "removing matched pairs from ends" but here we can choose any i, not just ends.
            // However, choosing i>1 means we remove inner symmetric pairs, which is like removing from a shorter prefix and suffix.
            // This can be simulated by DP: DP[l][r] = max over i from 1 to (r-l+1)/2 of (score for pair (l+i-1, r-i+1) + DP[l][l+i-2] + DP[l+i][r-i] + DP[r-i+2][r]).
            // Again messy.

            // Let's search for known problem: "three times each, remove symmetric positions, maximize same pairs".
            // This is actually equivalent to: we can take any matching of cards such that in the sequence of operations, the pairs removed are symmetric at the time of removal. This is similar to "non‑crossing matching" with symmetry constraint.
            // Another viewpoint: Consider the final set of scored pairs. For each scored pair (x,y), at the moment they were removed, they were at symmetric positions. This implies that in the original sequence, between x and y, the number of cards removed before them on the left equals the number removed before them on the right.
            // This is equivalent to: if we assign a weight +1 to left removal and -1 to right removal, then the balance between x and y must be zero.
            // Actually, let’s define a process: we remove cards in some order. Let’s denote by L the set of cards removed as "left i-th", and R those removed as "right i-th". Each operation removes one from L and one from R. For a scored pair (p,q), p is removed as left i-th, q as right i-th for same i.
            // So p and q are removed simultaneously. So they must be at symmetric positions in the current array.
            // This is equivalent to: in the original sequence, let’s denote by a the number of cards before p that are removed in earlier steps as left removals, and b the number of cards before p that are removed as right removals. Similarly for q.
            // The symmetric condition: i = position of p from left = a+1, position of q from right = b+1, and they are same i, so a = b.
            // Also, the cards removed before them must be consistent.
            // This leads to a DP on intervals: DP[l][r] = max score for subarray [l,r] where we consider cards that are removed in some order, but we can think of removing from both ends gradually.
            // Actually, the operation is symmetric: removing i-th from left and i-th from right essentially removes a prefix of length i and a suffix of length i, but only the i-th elements are removed, the others remain? Wait, no: only two cards are removed, not whole prefix/suffix.
            // So it's not removing prefix/suffix.

            // Given complexity N<=2000, O(N^2) DP is expected.
            // Let's try interval DP: DP[l][r] = max score for subsequence from l to r inclusive.
            // Consider the last operation in this interval. Suppose the last operation removes positions p and q (l <= p < q <= r) with seq[p]==seq[q], and at the time of removal, they were symmetric in the current subarray. That means that in the subarray [l,r], the number of cards before p that are not yet removed equals the number of cards after q that are not yet removed.
            // But this is complicated.

            // Let's think greedy? Since each number appears three times, maybe we can always score at least N? Not sure.

            // Let's attempt a different DP: Let’s reorder indices. The operation is: choose i, remove positions i and len-i+1 (1‑based). This is like removing from both ends with offset i-1.
            // So effectively, we are pairing positions (i, len-i+1) for some i in the current array.
            // This is similar to: we can pair positions that are symmetric in the current array.
            // This is exactly the same as: we can take a set of disjoint pairs (x,y) such that in the sequence of removals, when we remove pair (x,y), the number of cards remaining before x equals the number remaining after y.
            // This is equivalent to: if we denote by t(x) the time when x is removed, then for a scored pair (x,y), we have t(x)=t(y) and at that time, count of cards before x not yet removed = count of cards after y not yet removed.
            // This is like a matching with constraints.

            // Given time, let's implement a known correct solution for this problem (recognized as AtCoder ABC 279 F? No).
            // Actually this is AtCoder ABC 266 F? Let's recall: "Three Cards" problem.
            // I remember solution: DP[l][r] = max score for interval [l,r].
            // Transition: either skip l (i.e., l is removed in some later operation not scored), or pair l with some k where seq[l]==seq[k] and (k-l-1) is even? Wait.

            // Let's derive: Suppose we remove pair (l, k) as symmetric in current array. At that moment, the array is [l, r]. For them to be symmetric, the number of cards before l that are already removed must equal the number of cards after k that are already removed. Since we are processing from outside in, we can assume we remove cards from ends gradually.
            // Actually, think recursively: In interval [l,r], we can remove pair (l, r) if they match, score+1, then solve [l+1, r-1].
            // Or we can remove some other symmetric pair: suppose we remove (l+i, r-i) for i>0. But then cards l..l+i-1 and r-i+1..r remain. However, after removing (l+i, r-i), the remaining array is [l, l+i-1] + [l+i+1, r-i-1] + [r-i+1, r]. This is three separate segments. But further operations can combine across segments because they become adjacent. So we cannot split.

            // Given the difficulty, I'll implement a known accepted solution from memory:
            // Let dp[l][r] = max score for subarray [l, r] (inclusive).
            // We consider two cases:
            // 1. l and r are paired in some operation: then they must be removed at same time, so they must be symmetric at that time, meaning the number of cards removed before l equals number removed after r. Since we are processing dp[l][r], we assume all cards outside [l,r] are already removed. So for l and r to be symmetric in current array, the current array is exactly [l,r], so they are symmetric only if l and r are the only cards? No, they are symmetric if the current array length is (r-l+1) and we choose i=1, so they are ends. So pairing l and r is allowed only if we choose i=1 at first step in this interval. So dp[l][r] = (seq[l]==seq[r]) + dp[l+1][r-1].
            // 2. We don't pair l and r now. Then either l is paired with some k inside, or r is paired with some k inside, or both.
            // Actually, we can split at some m: dp[l][r] = max(dp[l][m] + dp[m+1][r]).
            // This is standard interval DP.
            // So recurrence: dp[l][r] = max( dp[l+1][r-1] + (seq[l]==seq[r]), max_{m=l}^{r-1} dp[l][m] + dp[m+1][r] ).
            // This is O(N^3) too slow for N=2000.
            // Need O(N^2).

            // Wait, maybe we can use the fact that each number appears three times to reduce.
            // Let's think differently: Let’s precompute for each value its three positions.
            // We can choose to match two of them as a scored pair, leaving the third unmatched (or matched with others?).
            // Actually, each scored pair uses two cards of same value. The third card can be used in another pair with cards of same value? No, because only two cards of same value remain after using two in a pair.
            // So each value can contribute at most 1 to score (since three cards, you can only pair two of them, leaving one unpaired in scored pairs). But you could pair the third with another card of same value? No, only two cards left.
            // So each value can be scored at most once.
            // So we need to choose a set of values to score, and arrange operations to realize those pairs.
            // This becomes a maximum matching problem on intervals.

            // Given the time, I'll implement the O(N^2) DP that is known to work:
            // Let dp[l][r] = max score for interval [l, r] (inclusive).
            // Initialize dp[l][r] = 0 for l>r.
            // For len from 2 to M, for l from 0 to M-len, r=l+len-1.
            // 1. dp[l][r] = max(dp[l][r], dp[l+1][r-1] + (seq[l]==seq[r]))
            // 2. For k from l to r-1, dp[l][r] = max(dp[l][r], dp[l][k] + dp[k+1][r])
            // This is O(M^3) = 27e9 too big.

            // But we can optimize using that each value appears three times. Maybe we only need to consider k where seq[l]==seq[k] or seq[r]==seq[k].
            // Not sure.

            // Let's search memory: I think the correct solution is to use DP[l][r] where we consider removing from ends only, and the answer is dp[0][M-1].
            // Actually, there is a known problem "ABC 266 F" maybe.
            // Given the time, I'll output a plausible solution that might pass small N but not large.
            // But we need correct solution.

            // Let's think: The operation is symmetric, so we can think of the process as: we have a stack of operations. Equivalent to: we can take any matching of cards such that the matching is non‑crossing and symmetric in the sense that the two matched cards are equidistant from the center at the time of matching.
            // This is equivalent to: there exists a permutation of removals such that each matched pair (x,y) satisfies: in the original sequence, the number of cards before x that are removed before them equals the number of cards after y that are removed before them.
            // This is similar to: define a sequence of removals as a sequence of pairs (p,q). Let L be set of left removed cards, R right removed cards. For a pair (p,q) removed together, p in L, q in R. The condition: when we sort L by original index, and sort R by original index, then the i-th smallest in L and i-th smallest in R are removed together.
            // So we can think of matching the smallest remaining in L with smallest remaining in R, etc.
            // So essentially, we can choose any bipartite matching between cards removed as left and cards removed as right, with the constraint that if we pair p (from L) with q (from R), then at the time of removal, p is the a-th smallest in L and q is the a-th smallest in R.
            // This means that if we order all cards by original index, and assign each card a tag: L, R,
