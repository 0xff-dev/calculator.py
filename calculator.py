import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication,
                             QLineEdit, QPushButton, QGridLayout)
from PyQt5.QtGui import QRegExpValidator                       
from PyQt5.QtCore import Qt, QRegExp


class Calculator(QWidget):
    """
    计算器的基本页面的基本界面, 完成基本的计算
    """

    def __init__(self):
        super(Calculator, self).__init__()
        self.ui()
        self.char_stack = []     # 唯一的情况 1+-1=0
        self.num_stack = []
        self.nums = [chr(i) for i in range(48, 58)]
        self.operators = ['+', '-', '*', '/']

        self.empty_flag = True
        self.after_operator = False
        self.express = ''
        self.char_top = ''
        self.num_top = 0
        self.res = 0

        # >先计算, 为什么同样的符号改成了后计算, 是为了方便做一项操作,
        # 就是在你计算一个表达式之后，在继续按住等号, 以及会执行最后一次的符号运算
        self.priority_map = {
            '++': '>', '+-': '>', '-+': '>', '--': '>',
            '+*': '<', '+/': '<', '-*': '<', '-/': '<',
            '**': '>', '//': '>', '*+': '>', '/+': '>',
            '*-': '>', '/-': '>', '*/': '>', '/*': '>'
        }

    def ui(self):
        reg = QRegExp("^$")      # 把键盘禁用了, 仅可以按钮的输入
        validator = QRegExpValidator(reg, self)

        self.line_edit = QLineEdit('0', self)
        self.line_edit.setAlignment(Qt.AlignRight)
        self.line_edit.setValidator(validator)
        self.line_edit.setReadOnly(True)
        grid = QGridLayout()
        self.setLayout(grid)

        btn_names = [
            'C', 'None', '%', '/',
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '', '.', '='
        ]

        grid.addWidget(self.line_edit, 0, 0, 1, 4)
        positions = [(i, j) for i in range(1, 6) for j in range(4)]
        for pos, name in zip(positions, btn_names):
            if name == '':
                continue
            btn = QPushButton(name)
            btn.clicked.connect(self.show_msg)
            if name == '0':
                tmp_pos = (pos[0], pos[1]+1) 
                grid.addWidget(btn, *pos, 1, 2)
            else:
                grid.addWidget(btn, *pos)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle('Calculator')
        self.move(300, 150)
        self.show()

    def clear_line_edit(self):
        self.line_edit.clear()
        self.line_edit.setText('0')
        self.res = 0
        self.empty_flag = True
    
    def deal_num_btn(self, sender_text):
        if self.after_operator:
            self.line_edit.clear()
            self.after_operator = False
        _str = self.line_edit.text()
        if _str == '0' or _str == 'Error' or self.empty_flag:
            _str = ''
        self.line_edit.setText(_str+sender_text)
        self.empty_flag = False

    def deal_point_btn(self):
        _str = self.line_edit.text()
        self.empty_flag = False
        point_count = self.line_edit.text().count('.')
        if point_count == 0:
            _str += '.'
        self.line_edit.setText(_str)

    def deal_operator_btn(self, sender_text):
        # 操作符号 +, -, *, /
        self.empty_flag = False
        _str = self.line_edit.text()
        if _str == '0' or _str == 'Error':
            # 就是需要上一次的计算结果
            self.num_stack.append(self.res)
            self.char_stack.append(sender_text)
            self.express += (str(self.res)+sender_text)
        else:
            self.num_top = float(_str) if _str.count('.') != 0 \
                                            else int(_str)
            
            self.char_top = sender_text
            self.num_stack.append(self.num_top)
            num_stack_len, char_stack_len = len(self.num_stack), len(self.char_stack)
            if (num_stack_len != 0) and (num_stack_len == char_stack_len):
                #在这里处理类似 输入 1+- 这种情况就是 1-后一个字符替换前面的
                self.char_stack = self.char_stack[:]
                self.num_stack = self.num_stack[:-1]
            else:
                # 1+2*..... 类似输入
                if len(self.char_stack) == 0:
                    self.char_stack.append(self.char_top)
                else:
                    operator_cmp_key = self.char_stack[-1] + sender_text
                    if self.priority_map[operator_cmp_key] == '>':
                        print(self.num_stack, self.char_stack)
                        self.calculate(sender_text)
                    self.char_stack.append(sender_text)
                self.after_operator = True

    def deal_equal_btn(self):
        _str = self.line_edit.text()
        self.empty_flag = True
        try:
            tmp_num = float(_str) if _str.count('.') != 0 \
                                            else int(_str)
            self.num_stack.append(tmp_num)
            if len(self.num_stack) == 1:
                # 需要上一次的结果, num_top能改变
                self.char_stack.append(self.char_top)
                self.num_stack.append(self.num_top)
            else:
                self.num_top = tmp_num
        except Exception as e:
            self.num_stack.append(self.num_top)
            print('Error: {}'.format(e.args))
        self.calculate()
        self.num_stack.clear()
        self.char_stack.clear()

    def show_msg(self):
        # 这个函数的拆开, 分不同按钮处理， 一个函数太鸡毛的长了, 先把功能实现了，在拆
        sender = self.sender()
        sender_text = sender.text()

        if sender_text == 'C':
            self.clear_line_edit()
        elif sender_text in self.nums:
            self.deal_num_btn(sender_text)
        elif sender_text == '.':
            self.deal_point_btn()
        elif sender_text in self.operators:
            self.deal_operator_btn(sender_text)
        elif sender_text == '=':
            self.deal_equal_btn()

    def auxiliary_calculate(self, first_num, second_num, operator: str):
        if operator == '/':
            if second_num == 0:
                _str = 'Error'
                self.res = 0
                self.line_edit.setText(_str)
                return None
            else:
                return first_num / second_num
        elif operator == '*':
            return first_num * second_num
        elif operator == '+':
            return first_num + second_num
        else:
            return first_num - second_num

    def calculate(self, operator='='):
        if operator == '=':
            # 要最后的结果
            print(self.num_stack)
            print(self.char_stack)
            error_falg = False
            while len(self.char_stack) >= 1:
                n1 = self.num_stack.pop()
                n2 = self.num_stack.pop()
                op = self.char_stack.pop()
                result = self.auxiliary_calculate(n2, n1, op)
                if result is None:
                    self.num_stack.clear()
                    self.char_stack.clear()
                    error_falg = True
                    break
                else:
                    self.num_stack.append(result)
            if not error_falg:
                self.res = self.num_stack.pop()
                if self.res == int(self.res):
                    self.res = int(self.res)
                self.line_edit.setText(str(self.res))
            else:
                self.line_edit.setText('Error')
        else:
            op = self.char_stack.pop()
            while len(self.char_stack) >= 0 and (self.priority_map[op+operator] == '>'):
                n1 = self.num_stack.pop()
                n2 = self.num_stack.pop()
                result = self.auxiliary_calculate(n2, n1, op)
                if result is None:
                    self.num_stack.clear()
                    self.char_stack.clear()
                    break
                self.num_stack.append(self.auxiliary_calculate(n2, n1, op))
                try:
                    op = self.char_stack.pop()
                except Exception as e:
                    break
            self.res = self.num_stack[-1]
            if self.res == int(self.res):
                self.res = int(self.res)
            self.line_edit.setText(str(self.res))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cal = Calculator()
    sys.exit(app.exec_())
