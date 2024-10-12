from flask import Blueprint, render_template, request, g, flash
from flask.cli import with_appcontext
from app.controller.lexer import get_question, push_lexer_result
from app.controller.parser import parse_tokens, push_final_result


userBP = Blueprint('user',__name__)

lexer_result = ''
parser_result = ''
semantic_result = ''
final_result = 'test final result'
token_types = []

#用来跳转主页的路由地址
@userBP.route('/homepage', methods=['GET', 'POST'])
def homepage():
    lexer_result = ''
    parser_result = ''
    semantic_result = ''
    final_result = 'test final result'
    token_types = []
    token_values = []
    if request.method == 'GET':
        return render_template('homepage.html', title='算经解释器', header='算经解释器')
    else:

        question = request.form.get("question")

        
        #将用户输入的问题传到zlexer里，进行分析
        token_types, token_values = get_question(question)
        
        parser_result = parse_tokens(token_types, token_values)

        lexer_result = push_lexer_result()
        final_result = push_final_result()

        #print(g.question)
        #提交信息后跳转结果页面
        return render_template('result.html', question=question, lexer=lexer_result, parser= parser_result, semantic=semantic_result,final=final_result,title='计算结果', header='计算结果')
    
# 用来跳转程序说明的路由地址
@userBP.route('/instruction')
def instruction():
    return render_template('instruction.html')
    
    

