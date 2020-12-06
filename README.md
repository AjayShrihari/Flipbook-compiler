# Flipbook-compiler
A programming language and compiler for displaying a flipbook
## Explanation
A context free grammar (CFG) is a formal grammar which has the four following components: alphabet, a set of productions, a start symbol and a set of variables. Using the principles defined in our CFG, we can design a compiler that parses certain inputs based on the rules given in the CFG and calls certain routines to perform certain tasks in the code that is inputted to the compiler.


Here, the lexer is built with a lust of regex expressions, and a rule table is defined to allow the programmer to define the allowed types of input. The lexer outputs a list of tokens based on the requirements we define explicitly.

The Parser translates the BNF-like grammar syntax and inputs it to a top-down recursive descent parser, which builds a parse tree from top-to down, assuming the tree starts with the non-terminal.

## Running instructions

```
git clone https://github.com/AjayShrihari/Flipbook-compiler.git
conda create --name flipbook --file spec-file.txt
conda activate flipbook
pip install -r requirements.txt
python src/compiler.py
```
The input ``` input/input.flip ``` which contains the commands that are inputted into the flipbook. 
The output will be seen in ``` pdf/output_pdf.pdf ```, where the apple is moved onto the head of Newton in the pdf using different x and y coordinate offsets for display.

Current funcionality for the code includes a way to give in ``` 'NUM NUM ID NUM NUM ID NUM NUM' ```, which allows for the command:
```
startpage endpage image1 x_coordinate1 y_coordinate1 image2 x_coordinate2 y_coordinate2
```
This allows for ```image1``` and ```image2``` to be placed at the respective x and y coordinates inputted by the programmer in the .flip file. Any other string will throw an exception by the lexer and parser, which is dispayed in the prompt.

## Extensibility
This is an extremely small subset of what is possible using the code written. A list of rules is present in ```compiler.py``` which allows for a list of rules to be maintained, which can be inputted once the CFG rules are written in BNF form and inputted to the table. The list of permissible input types is present in the rule table, which is given as an input to the lexer-parser.
 An archetype of this can be in the following language snippet, to allow for the use of keywords like ```for```, ```if``` and other conditions and statements similar to those present in standard programming languages. For the following code snippet, we can define the CFG rules., which can be further added in the code  for extending the operations of the compiler to loops and complex conditionals.
 ```
 x, y = 0, 0
for i = start:end

{
    x=x+y  
    x=x-y
    if (y>100)
    {
        y = y + y
    }
    
    insert_image x y 
    new_page
}
 ```
 BNF for CFG rules
 ```
 x, y = 0, 0
program:=statement*
statement:=for | if | expr | insert | new_page
insert:= "insert_image" ID ID
new_page:= "new_page"
expr:= expr + ID | expr - ID | ID | NUMBER
for:= "for" ID = ID: ID { statement } 
if:= "if" (ID cond_op ID) { statement}
cond_op:= ">"|"<"|"=="
 ```
 
### Note: 
A knowledge of compilers, parse trees, lexers, tokenization, parsers and ASTs was not known, and the assignment was done in less than 12 hours after learning the basic concepts required for programming language and compiler design.
This code was inspired by the application of a calculator operation for compiler design in the [SRPRDPL package](https://github.com/zwegner/sprdpl) which was used for the recursive descent parser. 
