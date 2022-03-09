# Introduction
在ASIC设计与验证领域，DSL (Design Specific Language) 一个重要的功能就是code-generation。在很多应用环境里面，我们可以用一套DSL来生成多种不同的语言（抑或是同种语言不同功效，比如说RTL vs. UVM)

# Architecture
首先，如果是一个多语言的code-generation, 那么抛开DSL不谈。我们其实可以选择其中的一个语言作为host language. 然后通过parse host language 来做其他语言的生成。这样做的一大缺点就是单独语言可能有host language所不支持的功能或language construct. 虽然可以通过别的方式解决，例如Verilog里面用comment做PSL, 但这会让implementation 和 usage 都变得更加复杂，和less user-friendly.
而且因为会用到现有的parser, （或者自己写一个新的parser) 但是原本的host language 本身并不能区分原来自有的用途和DSL-specific 用途，那么我们只能依靠一定的 coding style 或 convention来实现。但过往的经验表明，大部分users可能会做到syntactically correct, 但很多时候不能做到 coding convention correct. 而且纠错会是非常的复杂，或者干脆是不可能。
还有一个需要考虑的问题就是，code generators 本身需要支持单独generation。这样我们在有需要的情况下，实现parallel processing。

# Implementation
这里我们讨论一下多种可以用来implement DSL的方法。

## JSON / YAML
这个是最直接的方法。大部分的DSL所要实现的功能是description / declaration。 所以一个Markup Langauge就可以实现这类功能。(Never use XML, XML 作为一个前端语言非常的差）

```
{
  register: {
    name: 'output_resolution',
    offset: 0,
    field: {
      name: 'horizontal',
      lsb: 0,
      size: 16
    },
    field: {
      name: 'vertical',
      lsb: 15,
      size: 16
    }
  }
}
```

这里面的一大有事就是，不管我们选择用任何语言来做DSL processor, 那个语言肯定都会有现成的parser 可以用。缺点就是Markup language本身缺乏运算和programming flow control的construct。

## JSON + erb (or Markup Language + templating engine)
这是上一种的延伸，加上templating engine 之后，我们就可以有运算，也可以有if, loop这类的flow control功能，也可以稍微复杂一点的code organization来实现一些code reuse。

```
{
% for i in 0...2
  register: {
    name: 'output_resolution_inst<%=i%>',
    offset: <%= 0 + i * 32%>,
    field: {
      name: 'horizontal',
      lsb: 0,
      size: 16
    },
    field: {
      name: 'vertical',
      lsb: 16,
      size: 16
    }
  }
% end
}
```

一个最明显的问题就是我们多了一个pre-processing的步骤。还有缺点就是现在我们用了两种语言，那么使用的人就需要学会两种语言，这永远都是一个需要考虑的问题。

## Javascript
这个与上一个类似，不过因为JS本身的data structure syntax就是JSON。所以我们依赖一种语言就可以实现上面的功能。缺点就是我不确定JS作为通用编程语言的库多不多。（作为互联网语言肯定是够的）

## 自定义Syntax
这个是自由度最高的方法，实现起来也是最复杂的。可以自行设计所需的语法来实现需要的功能。

```
# Capital lettered words are KEYWORD
REGISTER output_resolution {
  OFFSET 0
  FIELD horizontal {
    LSB 0
    SIZE 16
  }
  FIELD veritical {
    LSB 16
    SIZE 16
  }
}
```
这个例子比较简单，因为并没有运算和flow control. 但是，这样的话其实与JSON的功能并没有实质的区别。除非对syntax本身非常高的要求，不然并没有必要这么做。
至于parser本身。可以上述的例子可以手写一个简单的parser。不过如果那么做的话，对语言以后的延伸性有非常大的限制，其实是不可取的。不如一开始就用lex&yacc或者ANTLR这些parser generator。

## 用General Purpose语言来做Syntax Host Language
这里主要是说用ruby，python, 或node.js这类的scripting language. 因为是host language, 所以DSL本身的syntax受限于host syntax. 比如，不想要括号的话，那么我们就不能用python. 因为python的function call是需要括号的。
大部分这类的implementation都是要利用到meta-programming这个concept.
以下是一个Ruby的例子：
```
block 'sample_block' do
  for i in 0...3
    register "output_resolution_inst#{i}" do
      offset 0 + i*32
      field 'horizontal', :lsb => 0, :size => 16
      field 'vertical', :lsb => 16, :size => 16
    end
  end
end

sample_block sample_block0
sample_block sample_block1
```
**block, register, inst, offset, field** 在这里全是keyword, 但其实他们都是function, 以**block**为例，其实他的implementation 是
```
def block(name, &block)
  # create a class with "name"
  # execute &block to set default parameters for said class
end
```

**sample_block**在这里实际上也是一个function, 不过是dynamically created。作用就是instantiate 一个sample_block object.

# Other
DSL 本身的parsing 和 processing 最好是分开的。这个主要是出于软件维护的考量。(其实传统的language parser也是这么做的，parser用来generate AST, 而AST和language就没什么关系了，AST 才是用来generate assembly的。而不是language to assembly这样)
一个方法就是DSL的parser (这个parser可以包含一定的validation功能）来generate一个JSON based intermediate （可以理解成我们的AST) 然后其他的processing, 包括code generators都是以这个JSON intermediate作为input。
这样的有事就是，DSL本身可以根据需求迭代，但这不会影响到downstream的code generators。
