# Introduction
In ASIC design and DV, one of the uses for DSL is as a description language to be consumed for code generation among other things. This is especally true if we need to generate multiple languages from the same set of specification.

# Architecture
Although we are interested in multi-language code generation from the same set of a DSL spec. One other implementation method, is to parse one language domain, then generate into other language domains. However, a notable shortcoming is inability to specify extra parameters only needed in generation of a subset of language domains.
For example, for a register DSL, we might have some extra paramters that will only be used in UVM domain, but not RTL domain.
Furthermore, it's actually tedious for parse a specific part of a general language. For example, if we are to parse the register block in Verilog. Then parser needs to be designed revolving around coding style convention instead of a DSL grammar. This can be quite un-safe, since people can't be expected to constantly write "convention compliant" code. But it's much easier to ensure they are at least writing syntactically correct code.
Another consideration is regarding the code generators who will consume the DSL. It is of the utmost important to have capability to run the code generators separately, so we may support parallel processing.

# Implementation
There are quite a few ways to implement a DSL.
## JSON / YAML
This is the most naive implementation:
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
This is very easy to parse as most languages already have a JSON parser module of some sort. However, this lacks capability for algorithmic processing.

## JSON + erb (or YAML + any templating engine)
This augments the previous implementation with scalability, even more complicated computation, and code-resue posibilities.
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

Drawback is the addition of an extra preprocessing step. Fortunately, the preprocessing only needs to be done once if we are generating multiple languages. Another draw back is on the maintanence side, since every user now needs to understand both the DSL and the templating engine being used.

## Javascript
In essence, we can view this as JSON + Javascript. But since JSON is almost native in JS, we have a monolithic language. Drawback (maybe) is the lack of open source packages for scripting needs. (Availability of web app related packages in JS is second to none, obviously, but I don't know if the same can be said when used as a general-purpose scripting language)

## Arbitrary Syntax
Obviously, this has the most amount of flexibility since one have complete freedom over grammar specification (still needs to avoid ambiguity.)

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

This does not look so different from the JSON implementation. Most of the time, it probably will not be so different. Drawback is obviously the complexity of implementing a parser. There are two methods of parser implementation, for simple grammars, one may write a naive parser. However, this will severely limit the flexibility of the language. From a practical point of view, this does not make much sense compared to the JSON option. One may really hate how JSON / YAML syntax reads. Another way is to use a lexer/parser generator such as lex and yacc. This is more complicated, but allows the most freedom. One may implement arithmetic support, programming control support (if's, loops, functions) if one choose to.

## Use an existing language as a hosting language
Common host language is probably some sort of scripting language, Python, Ruby, Node.js. Since we are using an existing language, the final DSL syntax is limited by the host syntax. The possibility of a hybrid arbitrary syntax + host syntax is also possible, but this adds some really bizzare complexity, which I do not recommend.

This will may heavily lean on the concept of metaprogramming. 

Below is an example using Ruby:
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

Here, **block, register, inst, offset, field** are all keywords implemented as functions. **block** is a function that creates a new Class with the name supplied. It will also execute the code block supplied and initialize the contents. **sample_block** may use the method_missing function to instantiate the sample_block class.

# Other
The parsing and processing of the DSL should be separated. In fact, an argument can be made where the code generators should always consume a "simple" syntax such as JSON based DSL. A host language based DSL will serve as the interface for the user because of its flexibility of ease of use, it can be used to generate a JSON intermediate which is then passed to the consumers.
This consideration arises from a software engineering perspective. The development and maintenance of the DSL parser and consumers can be easily separated this way.
