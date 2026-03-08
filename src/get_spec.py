import requests
from bs4 import BeautifulSoup

def get_spec(problem_id):

    problem_id='02547'

    url = f"https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id={problem_id}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # AOJ 页面正文在 class="problem_description"
    desc = soup.find("div", class_="problem_description")

    if not desc:
        print("未找到题面")
        return None

    text = desc.get_text("\n", strip=True)
    return text


if __name__ == "__main__":
    pid = "02547"   # 例如 p02547 -> 02547
    spec = get_spec(pid)

    if spec:
        with open(f"spec_{pid}.txt", "w", encoding="utf-8") as f:
            f.write(spec)

        print(spec)