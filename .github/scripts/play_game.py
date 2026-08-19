import os
import sys
import re

BOARD_START = "<!-- START_TICTACTOE -->"
BOARD_END = "<!-- END_TICTACTOE -->"

# Cell representations
EMPTY = " "
USER = "X"
AI = "O"

ICONS = {
    EMPTY: "⬜",
    USER: "⚡", # Electric for Zalana / Player
    AI: "🤖"    # AI
}

def render_board(board, status_msg="Your turn! Click an empty block ⚡"):
    md = f"{BOARD_START}\n"
    md += f"<div align=\"center\">\n\n"
    md += f"### 🎮 PLAY WITH AI // TIC-TAC-TOE\n"
    md += f"*{status_msg}*\n\n"
    md += "<table>\n"
    for r in range(3):
        md += "  <tr>\n"
        for c in range(3):
            val = board[r][c]
            if val == EMPTY:
                issue_title = f"game|play|{r},{c}"
                link = f"https://github.com/zalana28/zalana28/issues/new?title={issue_title}&body=Just+press+%27Submit+new+issue%27+to+make+your+move!"
                cell_content = f"<a href=\"{link}\"><img src=\"https://raw.githubusercontent.com/zalana28/zalana28/main/assets/blank.png\" width=\"50\" height=\"50\" alt=\"Square\" />⬜</a>"
            elif val == USER:
                cell_content = "<h2>⚡</h2>"
            else:
                cell_content = "<h2>🤖</h2>"
            md += f"    <td align=\"center\" width=\"70\" height=\"70\">{cell_content}</td>\n"
        md += "  </tr>\n"
    md += "</table>\n\n"
    reset_link = "https://github.com/zalana28/zalana28/issues/new?title=game|reset&body=Just+press+%27Submit+new+issue%27+to+reset+the+game!"
    md += f"[🔄 Reset Game]({reset_link})\n\n"
    md += "</div>\n"
    md += f"{BOARD_END}"
    return md

def check_winner(b):
    for r in range(3):
        if b[r][0] == b[r][1] == b[r][2] != EMPTY:
            return b[r][0]
    for c in range(3):
        if b[0][c] == b[1][c] == b[2][c] != EMPTY:
            return b[0][c]
    if b[0][0] == b[1][1] == b[2][2] != EMPTY:
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != EMPTY:
        return b[0][2]
    if all(b[r][c] != EMPTY for r in range(3) for c in range(3)):
        return "TIE"
    return None

def minimax(b, is_max):
    winner = check_winner(b)
    if winner == AI:
        return 10
    if winner == USER:
        return -10
    if winner == "TIE":
        return 0

    if is_max:
        best = -1000
        for r in range(3):
            for c in range(3):
                if b[r][c] == EMPTY:
                    b[r][c] = AI
                    best = max(best, minimax(b, False))
                    b[r][c] = EMPTY
        return best
    else:
        best = 1000
        for r in range(3):
            for c in range(3):
                if b[r][c] == EMPTY:
                    b[r][c] = USER
                    best = min(best, minimax(b, True))
                    b[r][c] = EMPTY
        return best

def find_best_move(b):
    best_val = -1000
    best_move = None
    for r in range(3):
        for c in range(3):
            if b[r][c] == EMPTY:
                b[r][c] = AI
                move_val = minimax(b, False)
                b[r][c] = EMPTY
                if move_val > best_val:
                    best_val = move_val
                    best_move = (r, c)
    return best_move

def parse_readme(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    board = [[EMPTY for _ in range(3)] for _ in range(3)]
    if BOARD_START in content and BOARD_END in content:
        section = content.split(BOARD_START)[1].split(BOARD_END)[0]
        # Parse rows
        rows = section.split("<tr>")[1:]
        for r_idx, row in enumerate(rows[:3]):
            cells = row.split("<td")[1:]
            for c_idx, cell in enumerate(cells[:3]):
                if "⚡" in cell:
                    board[r_idx][c_idx] = USER
                elif "🤖" in cell:
                    board[r_idx][c_idx] = AI
                else:
                    board[r_idx][c_idx] = EMPTY
    return content, board

def update_readme(file_path, new_game_md):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if BOARD_START in content and BOARD_END in content:
        pattern = re.compile(f"{re.escape(BOARD_START)}.*?{re.escape(BOARD_END)}", re.DOTALL)
        new_content = pattern.sub(new_game_md, content)
    else:
        new_content = content + "\n\n---\n\n" + new_game_md

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    issue_title = sys.argv[1] if len(sys.argv) > 1 else ""
    readme_path = sys.argv[2] if len(sys.argv) > 2 else "README.md"

    content, board = parse_readme(readme_path)

    if "game|reset" in issue_title:
        board = [[EMPTY for _ in range(3)] for _ in range(3)]
        msg = "Game reset! Your turn (Player ⚡)"
    elif "game|play|" in issue_title:
        coords = issue_title.split("game|play|")[1].strip()
        try:
            r, c = map(int, coords.split(","))
            if 0 <= r < 3 and 0 <= c < 3 and board[r][c] == EMPTY:
                board[r][c] = USER
                winner = check_winner(board)
                if winner == USER:
                    msg = "🎉 YOU WON! Well played, champion ⚡"
                elif winner == "TIE":
                    msg = "🤝 IT'S A TIE! Good match!"
                else:
                    # AI Move
                    ai_move = find_best_move(board)
                    if ai_move:
                        board[ai_move[0]][ai_move[1]] = AI
                        winner = check_winner(board)
                        if winner == AI:
                            msg = "🤖 AI WON! Better luck next time!"
                        elif winner == "TIE":
                            msg = "🤝 IT'S A TIE! Good match!"
                        else:
                            msg = f"AI moved to ({ai_move[0]},{ai_move[1]}). Your turn ⚡"
                    else:
                        msg = "Game over."
            else:
                msg = "Invalid move! Spot already taken."
        except Exception as e:
            msg = f"Error processing move: {e}"
    else:
        board = [[EMPTY for _ in range(3)] for _ in range(3)]
        msg = "Ready to play! You are ⚡ (Player), AI is 🤖"

    new_game_md = render_board(board, msg)
    update_readme(readme_path, new_game_md)
    print("README updated successfully!")

if __name__ == "__main__":
    main()
