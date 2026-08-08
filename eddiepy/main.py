from pathlib import Path
import ast
import random as random_module
import re
import sys
import time as time_module


# =========================================================
# EddieLang 錯誤
# =========================================================

class EddieLangError(Exception):
    """EddieLang 語法或執行錯誤。"""

    def __init__(self, message, line_number=None):
        self.message = message
        self.line_number = line_number
        super().__init__(message)


class BreakSignal(Exception):
    """
    用來通知迴圈立刻停止。

    這不是一般錯誤，而是直譯器內部使用的訊號。
    """
    pass


class ContinueSignal(Exception):
    """用來通知迴圈跳過本次迭代，直接進入下一輪。"""

    pass


class ReturnSignal(Exception):
    """用來把函數的回傳值傳回呼叫處。"""

    def __init__(self, value=None):
        self.value = value
        super().__init__()


# =========================================================
# 整理原始碼
# =========================================================

def normalize_source(code):
    """
    把同一行的大括號拆開。

    例如：

        如果 hp>0 {
            說 "OK"
        } 否則 {
            說 "NO"
        }

    會整理成：

        如果 hp>0
        {
        說 "OK"
        }
        否則
        {
        說 "NO"
        }

    字串裡的大括號不會被拆開。
    """

    result = []

    for line_number, original_line in enumerate(
        code.splitlines(),
        start=1
    ):
        current = ""
        quote = None
        escaped = False

        for character in original_line:
            # 目前正在字串裡
            if quote is not None:
                current += character

                if escaped:
                    escaped = False
                    continue

                if character == "\\":
                    escaped = True
                    continue

                if character == quote:
                    quote = None

                continue

            # 字串開始
            if character in ('"', "'"):
                quote = character
                current += character
                continue

            # 註解開始
            if character == "#":
                break

            # 大括號
            if character in ("{", "}"):
                if current.strip():
                    result.append(
                        {
                            "text": current.strip(),
                            "line": line_number
                        }
                    )

                result.append(
                    {
                        "text": character,
                        "line": line_number
                    }
                )

                current = ""
                continue

            current += character

        if quote is not None:
            raise EddieLangError(
                "字串缺少結尾引號",
                line_number
            )

        if current.strip():
            result.append(
                {
                    "text": current.strip(),
                    "line": line_number
                }
            )

    return result


# =========================================================
# 運算式 Tokenizer
# =========================================================

TOKEN_PATTERN = re.compile(
    r"""
    \s*
    (
        >=
        | <=
        | ==
        | !=
        | [+\-*/><()]
        | "(?:\\.|[^"\\])*"
        | '(?:\\.|[^'\\])*'
        | \d+\.\d+
        | \d+
        | [A-Za-z_\u4e00-\u9fff]
          [A-Za-z0-9_\u4e00-\u9fff]*
    )
    """,
    re.VERBOSE
)


def tokenize_expression(expression, line_number):
    """
    把運算式拆成 Token。

    例如：

        hp+10

    會變成：

        hp
        +
        10
    """

    expression = expression.strip()

    if expression == "":
        raise EddieLangError(
            "運算式不能是空的",
            line_number
        )

    tokens = []
    position = 0

    while position < len(expression):
        match = TOKEN_PATTERN.match(
            expression,
            position
        )

        if match is None:
            bad_character = expression[position]

            raise EddieLangError(
                f"運算式中有看不懂的符號：{bad_character}",
                line_number
            )

        tokens.append(match.group(1))
        position = match.end()

    return tokens


# =========================================================
# 運算式解析器
# =========================================================

class ExpressionParser:
    def __init__(
        self,
        tokens,
        variables,
        line_number
    ):
        self.tokens = tokens
        self.variables = variables
        self.line_number = line_number
        self.position = 0

    def current(self):
        if self.position >= len(self.tokens):
            return None

        return self.tokens[self.position]

    def consume(self, expected=None):
        token = self.current()

        if token is None:
            raise EddieLangError(
                "運算式不完整",
                self.line_number
            )

        if expected is not None and token != expected:
            raise EddieLangError(
                f"預期 {expected}，但收到 {token}",
                self.line_number
            )

        self.position += 1
        return token

    def parse(self):
        value = self.parse_comparison()

        if self.current() is not None:
            raise EddieLangError(
                f"多餘的內容：{self.current()}",
                self.line_number
            )

        return value

    # -----------------------------------------------------
    # 比較運算
    # -----------------------------------------------------

    def parse_comparison(self):
        left = self.parse_addition()
        operator = self.current()

        if operator in (
            ">",
            "<",
            ">=",
            "<=",
            "==",
            "!="
        ):
            self.consume()
            right = self.parse_addition()

            if operator == "==":
                return left == right

            if operator == "!=":
                return left != right

            self.check_comparable(left, right)

            if operator == ">":
                return left > right

            if operator == "<":
                return left < right

            if operator == ">=":
                return left >= right

            if operator == "<=":
                return left <= right

        return left

    # -----------------------------------------------------
    # 加減
    # -----------------------------------------------------

    def parse_addition(self):
        value = self.parse_multiplication()

        while self.current() in ("+", "-"):
            operator = self.consume()
            right = self.parse_multiplication()

            if operator == "+":
                if (
                    self.is_number(value)
                    and self.is_number(right)
                ):
                    value = value + right

                elif (
                    isinstance(value, str)
                    and isinstance(right, str)
                ):
                    value = value + right

                else:
                    raise EddieLangError(
                        "加法兩邊的資料類型不相容",
                        self.line_number
                    )

            elif operator == "-":
                self.check_numbers(value, right)
                value = value - right

        return value

    # -----------------------------------------------------
    # 乘除
    # -----------------------------------------------------

    def parse_multiplication(self):
        value = self.parse_unary()

        while self.current() in ("*", "/"):
            operator = self.consume()
            right = self.parse_unary()

            self.check_numbers(value, right)

            if operator == "*":
                value = value * right

            elif operator == "/":
                if right == 0:
                    raise EddieLangError(
                        "不能除以 0",
                        self.line_number
                    )

                value = value / right

        return value

    # -----------------------------------------------------
    # 負數
    # -----------------------------------------------------

    def parse_unary(self):
        if self.current() == "-":
            self.consume("-")
            value = self.parse_unary()

            if not self.is_number(value):
                raise EddieLangError(
                    "負號後面必須是數字",
                    self.line_number
                )

            return -value

        return self.parse_primary()

    # -----------------------------------------------------
    # 數字、字串、變數、括號
    # -----------------------------------------------------

    def parse_primary(self):
        token = self.current()

        if token is None:
            raise EddieLangError(
                "運算式不完整",
                self.line_number
            )

        # 括號
        if token == "(":
            self.consume("(")
            value = self.parse_comparison()
            self.consume(")")
            return value

        self.consume()

        # 字串
        if (
            token.startswith('"')
            or token.startswith("'")
        ):
            try:
                return ast.literal_eval(token)

            except (ValueError, SyntaxError):
                raise EddieLangError(
                    "字串格式錯誤",
                    self.line_number
                )

        # 布林值
        if token == "true":
            return True

        if token == "false":
            return False

        if token in ("None", "none"):
            return None

        # 小數
        if re.fullmatch(r"\d+\.\d+", token):
            return float(token)

        # 整數
        if re.fullmatch(r"\d+", token):
            return int(token)

        # 變數
        if token in self.variables:
            return self.variables[token]["value"]

        raise EddieLangError(
            f"未定義變數：{token}",
            self.line_number
        )

    @staticmethod
    def is_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )

    def check_numbers(self, left, right):
        if not self.is_number(left):
            raise EddieLangError(
                "左邊不是數字類型",
                self.line_number
            )

        if not self.is_number(right):
            raise EddieLangError(
                "右邊不是數字類型",
                self.line_number
            )

    def check_comparable(self, left, right):
        if (
            self.is_number(left)
            and self.is_number(right)
        ):
            return

        if (
            isinstance(left, str)
            and isinstance(right, str)
        ):
            return

        raise EddieLangError(
            "比較運算兩邊的資料類型不相容",
            self.line_number
        )


# =========================================================
# EddieLang 直譯器
# =========================================================

class EddieInterpreter:
    def __init__(self, code):
        self.lines = normalize_source(code)
        self.variables = {}
        self.functions = {}
        self.gui_root = None
        self.gui_started = False
        self.gui_entries = {}
        self.gui_entry_widgets = []
        self.gui_labels = []
        self.game_board = None
        self.game_canvas = None
        self.game_key = ""

        # 記錄目前位於幾層迴圈中
        self.loop_depth = 0
        self.function_depth = 0

    # -----------------------------------------------------
    # 運算式
    # -----------------------------------------------------

    def evaluate_expression(
        self,
        expression,
        line_number
    ):
        input_box_expression = re.fullmatch(
            r"輸入框\s*\((.*)\)",
            expression.strip()
        )

        if input_box_expression:
            arguments = self.split_arguments(
                input_box_expression.group(1),
                line_number
            )

            if len(arguments) != 1:
                raise EddieLangError(
                    "輸入框作為運算式時格式：輸入框(\"提示文字\")",
                    line_number
                )

            prompt = self.evaluate_expression(
                arguments[0],
                line_number
            )

            # GUI 輸入框必須嵌在主視窗中，不再跳出第二個對話視窗。
            entry = self.create_gui_input_widget(prompt, line_number)
            self.gui_entry_widgets.append(entry)
            return ""

        window_call = re.fullmatch(
            r"(?:開視窗|window)\s*\((.*)\)",
            expression.strip()
        )

        if window_call:
            arguments = self.split_arguments(
                window_call.group(1),
                line_number
            )

            if len(arguments) not in (0, 1, 2, 3):
                raise EddieLangError(
                    "開視窗格式錯誤，例如：開視窗(\"我的視窗\", 600, 400)",
                    line_number
                )

            title = "EddieLang"
            width = 600
            height = 400

            values = [
                self.evaluate_expression(argument, line_number)
                for argument in arguments
            ]

            if len(values) == 1:
                if not isinstance(values[0], str):
                    raise EddieLangError(
                        "開視窗的單一引數必須是標題文字",
                        line_number
                    )
                title = values[0]

            elif len(values) == 2:
                width, height = values

            elif len(values) == 3:
                title, width, height = values

            if not isinstance(title, str):
                raise EddieLangError(
                    "開視窗的標題必須是 str",
                    line_number
                )

            for value, label in ((width, "寬度"), (height, "高度")):
                if (
                    not isinstance(value, int)
                    or isinstance(value, bool)
                    or value <= 0
                ):
                    raise EddieLangError(
                        f"開視窗的{label}必須是正整數",
                        line_number
                    )

            try:
                import tkinter as tk
            except ImportError:
                raise EddieLangError(
                    "目前的 Python 沒有安裝 tkinter，無法開啟視窗",
                    line_number
                )

            try:
                root = tk.Tk()
                root.title(title)
                root.geometry(f"{width}x{height}")
                self.gui_root = root

            except tk.TclError as error:
                raise EddieLangError(
                    f"無法開啟視窗：{error}",
                    line_number
                )

            return None

        wait_call = re.fullmatch(
            r"(?:等待|sleep)\s*\((.*)\)",
            expression.strip()
        )

        if wait_call:
            arguments = self.split_arguments(
                wait_call.group(1),
                line_number
            )

            if len(arguments) != 1:
                raise EddieLangError(
                    "等待格式錯誤，例如：等待(2)",
                    line_number
                )

            seconds = self.evaluate_expression(
                arguments[0],
                line_number
            )

            if (
                not isinstance(seconds, (int, float))
                or isinstance(seconds, bool)
            ):
                raise EddieLangError(
                    "等待時間必須是數字",
                    line_number
                )

            if seconds < 0:
                raise EddieLangError(
                    "等待時間不能是負數",
                    line_number
                )

            time_module.sleep(seconds)
            return None

        time_call = re.fullmatch(
            r"(?:時間|time)\s*\(\s*\)",
            expression.strip()
        )

        if time_call:
            return time_module.time()

        random_call = re.fullmatch(
            r"(?:隨機|random)\s*\((.*)\)",
            expression.strip()
        )

        if random_call:
            arguments = self.split_arguments(
                random_call.group(1),
                line_number
            )

            if len(arguments) != 2:
                raise EddieLangError(
                    "隨機格式錯誤，例如：隨機(1, 100)",
                    line_number
                )

            minimum = self.evaluate_expression(
                arguments[0],
                line_number
            )
            maximum = self.evaluate_expression(
                arguments[1],
                line_number
            )

            for value, label in (
                (minimum, "最小值"),
                (maximum, "最大值")
            ):
                if not isinstance(value, int) or isinstance(value, bool):
                    raise EddieLangError(
                        f"隨機的{label}必須是 int",
                        line_number
                    )

            if minimum > maximum:
                raise EddieLangError(
                    "隨機的最小值不能大於最大值",
                    line_number
                )

            return random_module.randint(minimum, maximum)

        input_call = re.fullmatch(
            r"(?:輸入|input)\s*(?:\((.*)\))?",
            expression.strip()
        )

        if input_call:
            raw_prompt = input_call.group(1)
            prompt = ""

            if raw_prompt is not None and raw_prompt.strip():
                prompt_value = self.evaluate_expression(
                    raw_prompt.strip(),
                    line_number
                )
                prompt = str(prompt_value)

            return input(prompt)

        key_call = re.fullmatch(
            r"(?:取得按鍵|key)\s*\(\s*\)",
            expression.strip()
        )

        if key_call:
            key = self.game_key
            self.game_key = ""
            return key

        board_call = re.fullmatch(
            r"(?:取得棋盤|board)\s*\((.*)\)",
            expression.strip()
        )

        board_comparison = re.fullmatch(
            r"((?:取得棋盤|board)\s*\(.*\))\s*(==|!=|>=|<=|>|<)\s*(.+)",
            expression.strip()
        )

        if board_comparison:
            left = self.evaluate_expression(
                board_comparison.group(1),
                line_number
            )
            right = self.evaluate_expression(
                board_comparison.group(3),
                line_number
            )
            operator = board_comparison.group(2)

            if operator == "==":
                return left == right
            if operator == "!=":
                return left != right
            if operator == ">=":
                return left >= right
            if operator == "<=":
                return left <= right
            if operator == ">":
                return left > right
            return left < right

        if board_call:
            if self.game_board is None:
                raise EddieLangError("請先使用 建立棋盤()", line_number)

            arguments = self.split_arguments(
                board_call.group(1),
                line_number
            )
            if len(arguments) != 2:
                raise EddieLangError(
                    "取得棋盤格式：取得棋盤(x, y)",
                    line_number
                )

            x = self.evaluate_expression(arguments[0], line_number)
            y = self.evaluate_expression(arguments[1], line_number)

            if (
                not isinstance(x, int)
                or isinstance(x, bool)
                or not isinstance(y, int)
                or isinstance(y, bool)
                or y < 0
                or y >= len(self.game_board)
                or x < 0
                or x >= len(self.game_board[0])
            ):
                return 0

            return self.game_board[y][x]

        function_call = re.fullmatch(
            r"(?:呼叫|call)\s+[A-Za-z_\u4e00-\u9fff]"
            r"[A-Za-z0-9_\u4e00-\u9fff]*\s*\(.*\)",
            expression.strip()
        )

        if function_call:
            return self.execute_function_call(
                expression.strip(),
                line_number
            )

        tokens = tokenize_expression(
            expression,
            line_number
        )

        parser = ExpressionParser(
            tokens,
            self.variables,
            line_number
        )

        return parser.parse()

    # -----------------------------------------------------
    # 資料類型
    # -----------------------------------------------------

    @staticmethod
    def get_data_type(value):
        # bool 必須放在 int 前面
        if isinstance(value, bool):
            return "bool"

        if isinstance(value, int):
            return "int"

        if isinstance(value, float):
            return "float"

        if isinstance(value, str):
            return "str"

        if value is None:
            return "None"

        return "unknown"

    @staticmethod
    def is_valid_variable_name(name):
        return re.fullmatch(
            r"[A-Za-z_\u4e00-\u9fff]"
            r"[A-Za-z0-9_\u4e00-\u9fff]*",
            name
        ) is not None

    @staticmethod
    def is_input_expression(expression):
        return re.fullmatch(
            r"(?:輸入|input)\s*(?:\(.*\))?",
            expression.strip()
        ) is not None

    def convert_input_value(
        self,
        value,
        data_type,
        line_number
    ):
        if data_type == "str":
            return value

        try:
            if data_type == "int":
                return int(value)

            if data_type == "float":
                return float(value)

            if data_type == "bool":
                if value == "true":
                    return True

                if value == "false":
                    return False

        except (TypeError, ValueError):
            pass

        raise EddieLangError(
            f"輸入內容無法轉換成 {data_type}",
            line_number
        )

    # -----------------------------------------------------
    # 建立變數
    # -----------------------------------------------------

    def create_variable(
        self,
        data_type,
        variable_name,
        expression,
        line_number
    ):
        valid_types = (
            "int",
            "float",
            "str",
            "bool",
            "None",
            "none"
        )

        if data_type == "none":
            data_type = "None"

        if data_type not in valid_types:
            raise EddieLangError(
                f"未知資料類型：{data_type}",
                line_number
            )

        if not self.is_valid_variable_name(
            variable_name
        ):
            raise EddieLangError(
                f"不合法的變數名稱：{variable_name}",
                line_number
            )

        if variable_name in self.variables:
            raise EddieLangError(
                f"變數已經定義：{variable_name}",
                line_number
            )

        value = self.evaluate_expression(
            expression,
            line_number
        )

        if self.is_input_expression(expression):
            value = self.convert_input_value(
                value,
                data_type,
                line_number
            )

        actual_type = self.get_data_type(value)

        # float 可以接收 int
        if (
            data_type == "float"
            and actual_type == "int"
        ):
            value = float(value)
            actual_type = "float"

        if data_type != actual_type:
            raise EddieLangError(
                f"{data_type} 不能放入 {actual_type}",
                line_number
            )

        self.variables[variable_name] = {
            "type": data_type,
            "value": value
        }

    # -----------------------------------------------------
    # 修改變數
    # -----------------------------------------------------

    def assign_variable(
        self,
        variable_name,
        expression,
        line_number
    ):
        if variable_name not in self.variables:
            raise EddieLangError(
                f"未定義變數：{variable_name}",
                line_number
            )

        new_value = self.evaluate_expression(
            expression,
            line_number
        )

        old_type = self.variables[variable_name]["type"]

        if self.is_input_expression(expression):
            new_value = self.convert_input_value(
                new_value,
                old_type,
                line_number
            )

        new_type = self.get_data_type(new_value)

        # float 可以接收 int
        if old_type == "float" and new_type == "int":
            new_value = float(new_value)
            new_type = "float"

        if old_type != new_type:
            raise EddieLangError(
                f"變數 {variable_name} 是 {old_type}，"
                f"不能放入 {new_type}",
                line_number
            )

        self.variables[variable_name]["value"] = new_value

    # =====================================================
    # 解析整份程式
    # =====================================================

    def parse_program(self):
        nodes, next_index = self.parse_block(
            start_index=0,
            inside_braces=False
        )

        if next_index != len(self.lines):
            current = self.lines[next_index]

            raise EddieLangError(
                f"無法解析：{current['text']}",
                current["line"]
            )

        return nodes

    def parse_block(
        self,
        start_index,
        inside_braces
    ):
        nodes = []
        index = start_index

        while index < len(self.lines):
            item = self.lines[index]
            text = item["text"]
            line_number = item["line"]

            # 區塊結束
            if text == "}":
                if not inside_braces:
                    raise EddieLangError(
                        "多出了一個 }",
                        line_number
                    )

                return nodes, index + 1

            if text == "{":
                raise EddieLangError(
                    "這裡不應該出現 {",
                    line_number
                )

            # if
            if text.startswith("如果 "):
                node, index = self.parse_if_chain(index)
                nodes.append(node)
                continue

            # 函數
            if text.startswith("函數 "):
                node, index = self.parse_function(index)
                nodes.append(node)
                continue

            # 重複執行／while
            if (
                text.startswith("重複執行 ")
                or text.startswith("while ")
            ):
                node, index = self.parse_while(index)
                nodes.append(node)
                continue

            # for
            if (
                text.startswith("重複 ")
                or text.startswith("for ")
            ):
                node, index = self.parse_for(index)
                nodes.append(node)
                continue

            if (
                text.startswith("否則如果 ")
                or text == "否則"
            ):
                raise EddieLangError(
                    f"{text} 前面必須有 如果",
                    line_number
                )

            # 普通指令
            nodes.append(
                {
                    "kind": "statement",
                    "text": text,
                    "line": line_number
                }
            )

            index += 1

        if inside_braces:
            last_line = (
                self.lines[-1]["line"]
                if self.lines
                else 1
            )

            raise EddieLangError(
                "區塊缺少 }",
                last_line
            )

        return nodes, index

    # =====================================================
    # 解析函數
    # =====================================================

    def parse_function(self, start_index):
        item = self.lines[start_index]
        header = item["text"]
        line_number = item["line"]

        match = re.fullmatch(
            r"函數\s+([A-Za-z_\u4e00-\u9fff]"
            r"[A-Za-z0-9_\u4e00-\u9fff]*)\s*\((.*?)\)",
            header
        )

        if match is None:
            raise EddieLangError(
                "函數格式錯誤，例如：函數 歡迎(name)",
                line_number
            )

        function_name = match.group(1)
        raw_parameters = match.group(2).strip()
        parameters = []

        if raw_parameters:
            for parameter in raw_parameters.split(","):
                parameter = parameter.strip()

                if not self.is_valid_variable_name(parameter):
                    raise EddieLangError(
                        f"函數參數名稱不合法：{parameter}",
                        line_number
                    )

                if parameter in parameters:
                    raise EddieLangError(
                        f"函數參數重複：{parameter}",
                        line_number
                    )

                parameters.append(parameter)

        open_brace_index = start_index + 1

        if (
            open_brace_index >= len(self.lines)
            or self.lines[open_brace_index]["text"] != "{"
        ):
            raise EddieLangError(
                "函數標頭後面缺少 {",
                line_number
            )

        body, next_index = self.parse_block(
            start_index=open_brace_index + 1,
            inside_braces=True
        )

        return (
            {
                "kind": "function",
                "name": function_name,
                "parameters": parameters,
                "body": body,
                "line": line_number
            },
            next_index
        )

    # =====================================================
    # 解析 if / elif / else
    # =====================================================

    def parse_if_chain(self, start_index):
        branches = []
        else_body = None
        index = start_index

        while index < len(self.lines):
            item = self.lines[index]
            header = item["text"]
            line_number = item["line"]

            if header.startswith("如果 "):
                condition = header[len("如果 "):].strip()

            elif header.startswith("否則如果 "):
                condition = header[
                    len("否則如果 "):
                ].strip()

            elif header == "否則":
                condition = None

            else:
                break

            if condition == "":
                raise EddieLangError(
                    "如果 後面缺少條件",
                    line_number
                )

            open_brace_index = index + 1

            if (
                open_brace_index >= len(self.lines)
                or self.lines[open_brace_index]["text"] != "{"
            ):
                raise EddieLangError(
                    "條件後面缺少 {",
                    line_number
                )

            body, next_index = self.parse_block(
                start_index=open_brace_index + 1,
                inside_braces=True
            )

            if condition is None:
                else_body = body
                index = next_index
                break

            branches.append(
                {
                    "condition": condition,
                    "body": body,
                    "line": line_number
                }
            )

            index = next_index

            if index >= len(self.lines):
                break

            next_header = self.lines[index]["text"]

            if (
                next_header.startswith("否則如果 ")
                or next_header == "否則"
            ):
                continue

            break

        return (
            {
                "kind": "if",
                "branches": branches,
                "else_body": else_body
            },
            index
        )

    # =====================================================
    # 解析 while
    # =====================================================

    def parse_while(self, start_index):
        item = self.lines[start_index]
        header = item["text"]
        line_number = item["line"]

        if header.startswith("重複執行 "):
            condition = header[len("重複執行 "):].strip()
        else:
            condition = header[len("while "):].strip()

        if condition == "":
            raise EddieLangError(
                "while 後面缺少條件",
                line_number
            )

        open_brace_index = start_index + 1

        if (
            open_brace_index >= len(self.lines)
            or self.lines[open_brace_index]["text"] != "{"
        ):
            raise EddieLangError(
                "while 條件後面缺少 {",
                line_number
            )

        body, next_index = self.parse_block(
            start_index=open_brace_index + 1,
            inside_braces=True
        )

        return (
            {
                "kind": "while",
                "condition": condition,
                "body": body,
                "line": line_number
            },
            next_index
        )

    # =====================================================
    # 解析 for
    # =====================================================

    def parse_for(self, start_index):
        item = self.lines[start_index]
        header = item["text"]
        line_number = item["line"]

        # 支援：
        # 重複 i 從 1 到 5
        # for i 從 1 到 5
        # 重複 i 從 0 到 10 每次 2

        match = re.fullmatch(
            r"(?:重複|for)\s+"
            r"([A-Za-z_\u4e00-\u9fff]"
            r"[A-Za-z0-9_\u4e00-\u9fff]*)"
            r"\s+從\s+(.+?)"
            r"\s+到\s+(.+?)"
            r"(?:\s+每次\s+(.+))?",
            header
        )

        if match is None:
            raise EddieLangError(
                "for 格式錯誤，例如："
                "for i 從 1 到 5",
                line_number
            )

        variable_name = match.group(1)
        start_expression = match.group(2).strip()
        end_expression = match.group(3).strip()
        step_expression = match.group(4)

        if step_expression is not None:
            step_expression = step_expression.strip()

        open_brace_index = start_index + 1

        if (
            open_brace_index >= len(self.lines)
            or self.lines[open_brace_index]["text"] != "{"
        ):
            raise EddieLangError(
                "for 後面缺少 {",
                line_number
            )

        body, next_index = self.parse_block(
            start_index=open_brace_index + 1,
            inside_braces=True
        )

        return (
            {
                "kind": "for",
                "variable": variable_name,
                "start": start_expression,
                "end": end_expression,
                "step": step_expression,
                "body": body,
                "line": line_number
            },
            next_index
        )

    # =====================================================
    # 執行程式
    # =====================================================

    def run(self):
        nodes = self.parse_program()
        self.register_functions(nodes)
        self.execute_nodes(nodes)

        if self.gui_root is not None and not self.gui_started:
            self.gui_started = True
            self.gui_root.mainloop()

    def register_functions(self, nodes):
        for node in nodes:
            if node["kind"] == "function":
                if node["name"] in self.functions:
                    raise EddieLangError(
                        f"函數已經定義：{node['name']}",
                        node["line"]
                    )

                self.functions[node["name"]] = node

    def execute_nodes(self, nodes):
        for node in nodes:
            if node["kind"] == "function":
                continue

            if node["kind"] == "statement":
                self.execute_statement(
                    node["text"],
                    node["line"]
                )

            elif node["kind"] == "if":
                self.execute_if(node)

            elif node["kind"] == "while":
                self.execute_while(node)

            elif node["kind"] == "for":
                self.execute_for(node)

    def split_arguments(self, raw_arguments, line_number):
        if raw_arguments.strip() == "":
            return []

        arguments = []
        current = []
        quote = None
        depth = 0

        for character in raw_arguments:
            if quote is not None:
                current.append(character)

                if character == quote:
                    quote = None

                continue

            if character in ('"', "'"):
                quote = character
                current.append(character)
                continue

            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1

            if character == "," and depth == 0:
                argument = "".join(current).strip()

                if argument == "":
                    raise EddieLangError(
                        "函數引數不能是空白",
                        line_number
                    )

                arguments.append(argument)
                current = []
                continue

            current.append(character)

        if quote is not None or depth != 0:
            raise EddieLangError(
                "函數引數的括號或引號沒有關閉",
                line_number
            )

        argument = "".join(current).strip()

        if argument == "":
            raise EddieLangError(
                "函數引數不能是空白",
                line_number
            )

        arguments.append(argument)
        return arguments

    def execute_function_call(self, text, line_number):
        match = re.fullmatch(
            r"(?:呼叫|call)\s+([A-Za-z_\u4e00-\u9fff]"
            r"[A-Za-z0-9_\u4e00-\u9fff]*)\s*\((.*)\)",
            text
        )

        if match is None:
            raise EddieLangError(
                "呼叫格式錯誤，例如：呼叫 歡迎(\"Eddie\")",
                line_number
            )

        function_name = match.group(1)

        if function_name not in self.functions:
            raise EddieLangError(
                f"找不到函數：{function_name}",
                line_number
            )

        function = self.functions[function_name]
        arguments = self.split_arguments(match.group(2), line_number)
        parameters = function["parameters"]

        if len(arguments) != len(parameters):
            raise EddieLangError(
                f"函數 {function_name} 需要 {len(parameters)} 個引數，"
                f"但收到 {len(arguments)} 個",
                line_number
            )

        argument_values = [
            self.evaluate_expression(argument, line_number)
            for argument in arguments
        ]

        previous_variables = self.variables
        previous_loop_depth = self.loop_depth
        self.variables = {
            name: data.copy()
            for name, data in previous_variables.items()
        }

        for parameter, value in zip(parameters, argument_values):
            self.variables[parameter] = {
                "type": self.get_data_type(value),
                "value": value
            }

        self.function_depth += 1
        self.loop_depth = 0

        try:
            return_value = None

            try:
                self.execute_nodes(function["body"])

            except ReturnSignal as signal:
                return_value = signal.value

        finally:
            self.function_depth -= 1
            self.loop_depth = previous_loop_depth
            self.variables = previous_variables

        return return_value

    # =====================================================
    # 執行 if
    # =====================================================

    def execute_if(self, node):
        for branch in node["branches"]:
            result = self.evaluate_expression(
                branch["condition"],
                branch["line"]
            )

            if not isinstance(result, bool):
                raise EddieLangError(
                    "如果 後面的條件必須得到 bool",
                    branch["line"]
                )

            if result:
                self.execute_nodes(branch["body"])
                return

        if node["else_body"] is not None:
            self.execute_nodes(node["else_body"])

    # =====================================================
    # 執行 while
    # =====================================================

    def execute_while(self, node):
        loop_count = 0
        max_loop_count = 100000

        self.loop_depth += 1

        try:
            while True:
                result = self.evaluate_expression(
                    node["condition"],
                    node["line"]
                )

                if not isinstance(result, bool):
                    raise EddieLangError(
                        "while 後面的條件必須得到 bool",
                        node["line"]
                    )

                if not result:
                    break

                try:
                    self.execute_nodes(node["body"])

                except BreakSignal:
                    break

                except ContinueSignal:
                    # continue 仍算完成了一次迴圈，讓防無限迴圈計數正常運作。
                    pass

                loop_count += 1

                # 防止程式因無限迴圈完全卡住
                if loop_count >= max_loop_count:
                    raise EddieLangError(
                        "迴圈已執行 100000 次，"
                        "可能是無限迴圈",
                        node["line"]
                    )

        finally:
            self.loop_depth -= 1

    # =====================================================
    # 執行 for
    # =====================================================

    def execute_for(self, node):
        start_value = self.evaluate_expression(
            node["start"],
            node["line"]
        )

        end_value = self.evaluate_expression(
            node["end"],
            node["line"]
        )

        if (
            not isinstance(start_value, int)
            or isinstance(start_value, bool)
        ):
            raise EddieLangError(
                "for 的開始值必須是 int",
                node["line"]
            )

        if (
            not isinstance(end_value, int)
            or isinstance(end_value, bool)
        ):
            raise EddieLangError(
                "for 的結束值必須是 int",
                node["line"]
            )

        # 沒有寫「每次」時，自動決定方向
        if node["step"] is None:
            if start_value <= end_value:
                step_value = 1
            else:
                step_value = -1

        else:
            step_value = self.evaluate_expression(
                node["step"],
                node["line"]
            )

            if (
                not isinstance(step_value, int)
                or isinstance(step_value, bool)
            ):
                raise EddieLangError(
                    "for 的每次增加值必須是 int",
                    node["line"]
                )

        if step_value == 0:
            raise EddieLangError(
                "for 的每次增加值不能是 0",
                node["line"]
            )

        if (
            start_value < end_value
            and step_value < 0
        ):
            raise EddieLangError(
                "開始值小於結束值時，"
                "每次增加值不能是負數",
                node["line"]
            )

        if (
            start_value > end_value
            and step_value > 0
        ):
            raise EddieLangError(
                "開始值大於結束值時，"
                "每次增加值必須是負數",
                node["line"]
            )

        # 「到」包含最後一個數字
        if step_value > 0:
            stop_value = end_value + 1
        else:
            stop_value = end_value - 1

        variable_name = node["variable"]

        # 如果迴圈變數已存在，必須是 int
        if variable_name in self.variables:
            if (
                self.variables[variable_name]["type"]
                != "int"
            ):
                raise EddieLangError(
                    f"for 變數 {variable_name} 必須是 int",
                    node["line"]
                )

        else:
            self.variables[variable_name] = {
                "type": "int",
                "value": start_value
            }

        self.loop_depth += 1

        try:
            for value in range(
                start_value,
                stop_value,
                step_value
            ):
                self.variables[variable_name]["value"] = value

                try:
                    self.execute_nodes(node["body"])

                except BreakSignal:
                    break

                except ContinueSignal:
                    continue

        finally:
            self.loop_depth -= 1

    # =====================================================
    # 執行普通指令
    # =====================================================

    def execute_gui_statement(self, text, line_number):
        match = re.fullmatch(
            r"(顯示文字|輸入框|按鈕|顯示視窗)\s*\((.*)\)",
            text
        )

        if match is None:
            raise EddieLangError(
                "GUI 格式錯誤",
                line_number
            )

        command = match.group(1)
        arguments = self.split_arguments(
            match.group(2),
            line_number
        )

        if command == "顯示視窗":
            if arguments:
                raise EddieLangError(
                    "顯示視窗不需要引數",
                    line_number
                )

            if self.gui_root is None:
                raise EddieLangError(
                    "請先使用 開視窗()",
                    line_number
                )

            if not self.gui_started:
                self.gui_started = True
                self.gui_root.mainloop()

            return

        if self.gui_root is None:
            raise EddieLangError(
                "請先使用 開視窗()",
                line_number
            )

        try:
            import tkinter as tk
        except ImportError:
            raise EddieLangError(
                "目前的 Python 沒有安裝 tkinter，無法建立 GUI 元件",
                line_number
            )

        values = [
            self.evaluate_expression(argument, line_number)
            for argument in arguments
        ]

        if command in ("顯示文字", "輸入框", "按鈕"):
            if len(values) not in (1, 3):
                raise EddieLangError(
                    f"{command} 格式：{command}(\"內容\", x, y)",
                    line_number
                )

            position = None

            if len(values) == 3:
                x, y = values[1], values[2]
                if (
                    not isinstance(x, int)
                    or isinstance(x, bool)
                    or not isinstance(y, int)
                    or isinstance(y, bool)
                    or x < 0
                    or y < 0
                ):
                    raise EddieLangError(
                        f"{command} 的 x、y 必須是非負整數",
                        line_number
                    )
                position = (x, y)

            if command == "顯示文字":
                widget = tk.Label(
                    self.gui_root,
                    text=str(values[0]),
                    font=("Microsoft JhengHei", 14),
                    padx=12,
                    pady=10
                )
                self.gui_labels.append(widget)
            elif command == "輸入框":
                widget = tk.Entry(self.gui_root)
                self.gui_entry_widgets.append(widget)
            else:
                widget = tk.Button(
                    self.gui_root,
                    text=str(values[0]),
                    padx=12,
                    pady=6
                )

                def submit_input():
                    if not self.gui_entry_widgets or not self.gui_labels:
                        return

                    entered_value = self.gui_entry_widgets[0].get()
                    self.gui_labels[-1].configure(
                        text="哈摟 " + entered_value
                    )

                widget.configure(command=submit_input)

            if position is None:
                widget.pack(padx=12, pady=6)
            else:
                widget.place(x=position[0], y=position[1])
            return

    def create_gui_input_widget(self, prompt, line_number):
        if self.gui_root is None:
            raise EddieLangError(
                "請先使用 開視窗()",
                line_number
            )

        if not isinstance(prompt, str):
            raise EddieLangError(
                "輸入框提示文字必須是 str",
                line_number
            )

        try:
            import tkinter as tk
        except ImportError:
            raise EddieLangError(
                "目前的 Python 沒有安裝 tkinter，無法建立 GUI 輸入框",
                line_number
            )

        container = tk.Frame(self.gui_root)
        label = tk.Label(
            container,
            text=prompt,
            font=("Microsoft JhengHei", 12)
        )
        entry = tk.Entry(container, width=28)
        label.pack(side="left", padx=(0, 8))
        entry.pack(side="left")
        container.pack(anchor="w", padx=20, pady=8)
        return entry

    def read_gui_input(self, prompt, line_number):
        if self.gui_root is None:
            raise EddieLangError(
                "請先使用 開視窗()",
                line_number
            )

        if not isinstance(prompt, str):
            raise EddieLangError(
                "輸入框提示文字必須是 str",
                line_number
            )

        try:
            import tkinter as tk
            from tkinter import simpledialog
        except ImportError:
            raise EddieLangError(
                "目前的 Python 沒有安裝 tkinter，無法建立輸入框",
                line_number
            )

        try:
            self.gui_root.withdraw()
            value = simpledialog.askstring(
                "EddieLang 輸入",
                prompt,
                parent=self.gui_root
            )
            self.gui_root.deiconify()
            return value if value is not None else ""

        except tk.TclError as error:
            raise EddieLangError(
                f"無法開啟輸入框：{error}",
                line_number
            )

    def execute_game_statement(self, text, line_number):
        match = re.fullmatch(
            r"(建立棋盤|處理事件|畫棋盤|設定棋盤|清空棋盤)\s*\((.*)\)",
            text
        )

        if match is None:
            raise EddieLangError("遊戲指令格式錯誤", line_number)

        command = match.group(1)
        arguments = self.split_arguments(match.group(2), line_number)

        if self.gui_root is None:
            raise EddieLangError("請先使用 開視窗()", line_number)

        try:
            import tkinter as tk
        except ImportError:
            raise EddieLangError(
                "目前的 Python 沒有安裝 tkinter，無法建立遊戲棋盤",
                line_number
            )

        if command == "建立棋盤":
            if len(arguments) != 2:
                raise EddieLangError(
                    "建立棋盤格式：建立棋盤(寬度, 高度)",
                    line_number
                )

            width = self.evaluate_expression(arguments[0], line_number)
            height = self.evaluate_expression(arguments[1], line_number)

            if (
                not isinstance(width, int)
                or isinstance(width, bool)
                or not isinstance(height, int)
                or isinstance(height, bool)
                or width <= 0
                or height <= 0
            ):
                raise EddieLangError(
                    "棋盤寬度與高度必須是正整數",
                    line_number
                )

            self.game_board = [[0 for _ in range(width)] for _ in range(height)]
            self.game_canvas = tk.Canvas(
                self.gui_root,
                width=width * 30,
                height=height * 30,
                background="#111827",
                highlightthickness=0
            )
            self.game_canvas.pack(padx=12, pady=12)

            def on_key(event):
                key_map = {
                    "Left": "左",
                    "Right": "右",
                    "Up": "上",
                    "Down": "下",
                    "space": "空白"
                }
                self.game_key = key_map.get(event.keysym, event.keysym)

            self.gui_root.bind("<KeyPress>", on_key)
            self.gui_root.focus_force()
            return

        if command == "處理事件":
            if arguments:
                raise EddieLangError(
                    "處理事件不需要引數",
                    line_number
                )
            try:
                self.gui_root.update_idletasks()
                self.gui_root.update()
            except tk.TclError:
                raise SystemExit(0)
            return

        if command == "畫棋盤":
            if arguments:
                raise EddieLangError(
                    "畫棋盤不需要引數",
                    line_number
                )
            if self.game_board is None or self.game_canvas is None:
                raise EddieLangError(
                    "請先使用 建立棋盤()",
                    line_number
                )

            try:
                self.game_canvas.delete("all")
            except tk.TclError:
                # 視窗可能剛在處理事件後被關閉，安全結束 EddieLang 程式。
                raise SystemExit(0)
            for y, row in enumerate(self.game_board):
                for x, value in enumerate(row):
                    colors = {
                        0: "#263244",
                        1: "#00d9ff",
                        2: "#ffe000",
                        3: "#b000ff",
                        4: "#ff8c00",
                        5: "#246bff",
                        6: "#28d96f",
                        7: "#ff365d"
                    }
                    color = colors.get(value, "#ffffff")
                    self.game_canvas.create_rectangle(
                        x * 30 + 1,
                        y * 30 + 1,
                        (x + 1) * 30 - 1,
                        (y + 1) * 30 - 1,
                        fill=color,
                        outline="#111827"
                    )

        if command == "清空棋盤":
            if arguments:
                raise EddieLangError(
                    "清空棋盤不需要引數",
                    line_number
                )
            if self.game_board is None:
                raise EddieLangError(
                    "請先使用 建立棋盤()",
                    line_number
                )
            for y in range(len(self.game_board)):
                for x in range(len(self.game_board[0])):
                    self.game_board[y][x] = 0
            return

        if command == "設定棋盤":
            if len(arguments) != 3:
                raise EddieLangError(
                    "設定棋盤格式：設定棋盤(x, y, 值)",
                    line_number
                )
            x = self.evaluate_expression(arguments[0], line_number)
            y = self.evaluate_expression(arguments[1], line_number)
            value = self.evaluate_expression(arguments[2], line_number)

            if self.game_board is None:
                raise EddieLangError(
                    "請先使用 建立棋盤()",
                    line_number
                )
            if (
                not isinstance(x, int)
                or isinstance(x, bool)
                or not isinstance(y, int)
                or isinstance(y, bool)
                or not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise EddieLangError(
                    "設定棋盤的 x、y、值必須是整數",
                    line_number
                )
            if 0 <= y < len(self.game_board) and 0 <= x < len(self.game_board[0]):
                self.game_board[y][x] = value
            return

    def execute_statement(
        self,
        text,
        line_number
    ):
        if re.fullmatch(
            r"(?:等待|sleep)\s*\(.*\)",
            text
        ):
            self.evaluate_expression(text, line_number)
            return

        if re.fullmatch(
            r"(?:開視窗|window)\s*\(.*\)",
            text
        ):
            self.evaluate_expression(text, line_number)
            return

        if re.fullmatch(
            r"(?:顯示文字|輸入框|按鈕|顯示視窗)\s*\(.*\)",
            text
        ):
            self.execute_gui_statement(text, line_number)
            return

        if re.fullmatch(
            r"(?:建立棋盤|處理事件|畫棋盤|設定棋盤|清空棋盤)\s*\(.*\)",
            text
        ):
            self.execute_game_statement(text, line_number)
            return

        # -------------------------------------------------
        # 函數呼叫／回傳
        # -------------------------------------------------

        if text.startswith("呼叫 ") or text.startswith("call "):
            self.execute_function_call(text, line_number)
            return

        if text == "回傳" or text.startswith("回傳 "):
            if self.function_depth <= 0:
                raise EddieLangError(
                    "回傳只能寫在函數裡",
                    line_number
                )

            content = text[len("回傳"):].strip()
            value = None

            if content:
                value = self.evaluate_expression(content, line_number)

            raise ReturnSignal(value)

        # -------------------------------------------------
        # break／停止
        # -------------------------------------------------

        if text in ("停止", "break"):
            if self.loop_depth <= 0:
                raise EddieLangError(
                    "break 只能寫在迴圈裡",
                    line_number
                )

            raise BreakSignal()

        # -------------------------------------------------
        # 跳過／continue
        # -------------------------------------------------

        if text in ("跳過", "continue"):
            if self.loop_depth <= 0:
                raise EddieLangError(
                    "跳過只能寫在迴圈裡",
                    line_number
                )

            raise ContinueSignal()

        # -------------------------------------------------
        # 說
        # -------------------------------------------------

        if text == "說" or text.startswith("說 "):
            content = text[len("說"):].strip()

            if content == "":
                raise EddieLangError(
                    "說 後面要有字串、變數或運算式",
                    line_number
                )

            value = self.evaluate_expression(
                content,
                line_number
            )

            if isinstance(value, bool):
                print("true" if value else "false")
            else:
                print(value)

            return

        # -------------------------------------------------
        # 設定變數
        # -------------------------------------------------

        declaration_match = re.fullmatch(
            r"設定\s+"
            r"(int|float|str|bool|None|none)\s+"
            r"([A-Za-z_\u4e00-\u9fff]"
            r"[A-Za-z0-9_\u4e00-\u9fff]*)"
            r"\s*=\s*(.+)",
            text
        )

        if declaration_match:
            data_type = declaration_match.group(1)
            variable_name = declaration_match.group(2)
            expression = declaration_match.group(3)

            self.create_variable(
                data_type,
                variable_name,
                expression,
                line_number
            )

            return

        if text.startswith("設定"):
            raise EddieLangError(
                "設定格式錯誤，例如："
                "設定 int hp = 100",
                line_number
            )

        # -------------------------------------------------
        # 修改變數
        # 支援 hp=hp+10
        # -------------------------------------------------

        assignment_match = re.fullmatch(
            r"([A-Za-z_\u4e00-\u9fff]"
            r"[A-Za-z0-9_\u4e00-\u9fff]*)"
            r"\s*=\s*(.+)",
            text
        )

        if assignment_match:
            variable_name = assignment_match.group(1)
            expression = assignment_match.group(2)

            self.assign_variable(
                variable_name,
                expression,
                line_number
            )

            return

        # -------------------------------------------------
        # 舊版四則運算指令
        # -------------------------------------------------

        command_match = re.fullmatch(
            r"(加|減|乘|除)\s+(.+)",
            text
        )

        if command_match:
            command = command_match.group(1)
            content = command_match.group(2)

            operator_map = {
                "加": "+",
                "減": "-",
                "乘": "*",
                "除": "/"
            }

            operator = operator_map[command]

            # 支援：加 hp 10
            simple_match = re.fullmatch(
                r"(\S+)\s+(\S+)",
                content
            )

            if simple_match:
                expression = (
                    simple_match.group(1)
                    + operator
                    + simple_match.group(2)
                )
            else:
                expression = content

            value = self.evaluate_expression(
                expression,
                line_number
            )

            if isinstance(value, bool):
                print("true" if value else "false")
            else:
                print(value)

            return

        raise EddieLangError(
            f"看不懂的指令：{text}",
            line_number
        )


# =========================================================
# 執行 EddieLang
# =========================================================

def run_code(code):
    try:
        interpreter = EddieInterpreter(code)
        interpreter.run()

    except EddieLangError as error:
        if error.line_number is None:
            print(
                f"EddieLang 錯誤：{error.message}"
            )
        else:
            print(
                f"第 {error.line_number} 行錯誤："
                f"{error.message}"
            )

    except BreakSignal:
        # 正常情況不會到這裡。
        # 這是額外保護。
        print("EddieLang 錯誤：break 沒有被迴圈處理")

    except ContinueSignal:
        # 正常情況不會到這裡，代表 continue 出現在迴圈外。
        print("EddieLang 錯誤：continue 沒有被迴圈處理")


# =========================================================
# 主程式
# =========================================================

def main(file_argument=None):
    if file_argument is None:
        file_path = Path(__file__).with_name("main.eddie")
    else:
        file_path = Path(file_argument).expanduser()

    if not file_path.exists():
        print(f"找不到 EddieLang 檔案：{file_path}")
        return

    try:
        program = file_path.read_text(
            encoding="utf-8"
        )

    except OSError as error:
        print(
            f"讀取 main.eddie 失敗：{error}"
        )
        return

    run_code(program)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
