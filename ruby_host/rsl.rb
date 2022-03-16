$blocks = {}
$instantiations = []

def block(name, &cb)
    klass = Class.new(Block) do
        self.class_variable_set(:@@name, name)
        self.instance_eval(&cb)
    end
    
    $blocks[name.to_sym] = klass
    define_method name.to_sym do |*args|
        inst = {
            :name => name.to_sym,
            :inst => args[0]
        }

        $instantiations << inst
    end
end

def register(name, &cb)
    reg = Register.new(name)
    reg.instance_eval(&cb)

    self.registers << reg
end

def field(name, **opts)
    f = {}
    f[:name] = name
    
    opts.each_pair do |k,v|
        f[k.to_sym] = v
    end

    self.fields << f
end

module DSL
    def method_missing(m, *args, &block)
        unless block_given?
            self.params[m.to_sym] = args[0] 
        end
    end
end

class Block
    extend DSL
    @@name = 'base'
    @@type = 'block'
    @@registers = []

    def Block.registers
        @@registers
    end

    def Block.to_json
        h = {}
        h[:registers] = @@registers.collect do |r|
            r.to_json
        end 
        h[:name] = @@name

        h
    end
end

# One of the reasons to have a separate class for each register is because of scoping
class Register
    include DSL 
    attr_accessor :name, :fields, :params

    def initialize(name)
        @name = name
        @fields = []
        @params = {}
    end

    def to_json
        h = {}
        h[:fields] = @fields
        h[:name] = @name
        @params.each_pair do |k, v|
            h[k] = v
        end

        h
    end
end

def gen_json(blocks, instantiations)
    require 'json'
    blocks.each_pair do |k, v|
        puts JSON.pretty_generate(v.to_json)
    end

    puts JSON.pretty_generate(instantiations)
end

# MAIN
load "./#{ARGV[0]}"
gen_json($blocks, $instantiations)


