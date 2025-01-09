import argparse
import os

def addJsonItem2Argparser(parser,key, item):
    vType = item.get("type") 
    pName = item.get("name") if item.get("name") is not None else key
    desc = item.get("desc") if item.get("desc") is not None else f"Argument list for {key}"
    default = item.get("default") if item.get("default") is not None else None
    isRequired = item.get("required") if item.get("required") is not None else False
    if vType == "file":
        parser.add_argument(
            f'--{key}', 
            type=str, 
            nargs='+',  # 可以接受一个或多个参数
            help=desc
        )
    else:
        __t = str
        if vType == "double":
           __t = float 
        elif vType == "int":
            __t = int
        elif vType == "bool":
            __t = str2bool

        if(isRequired == False):
            nargs = "?"
        else:
            nargs = None
        
        if default is not None:
            parser.add_argument(
                f'--{key}', 
                type=__t, 
                nargs=nargs,  # 可以接受一个或多个参数
                default=default,
                help=desc
            )
        else:
            parser.add_argument(
                f'--{key}', 
                type=__t, 
                nargs=nargs,
                help=desc
            )



def addDict2Argparser(parser, default_dict):
    for k, v in default_dict.items():
        v_type = type(v)        
        # check if v is dict
        if isinstance(v, dict):
            # 说明是json的参数
            addJsonItem2Argparser(parser,k, v)        
        else:
            if v is None:
                v_type = str
            elif isinstance(v, bool):
                v_type = str2bool
            parser.add_argument(f"--{k}", default=v, type=v_type)


def args_to_dict(args, keys):
    return {k: getattr(args, k) for k in keys}

def str2bool(v):
    """
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("boolean value expected")
    

def loadJsonConfig(configs):
    import json
    with open(configs) as f:
        return json.load(f)
    return None

def loadPyConfig(configs, modelName="__model__"):
    import importlib.util
    spec = importlib.util.spec_from_file_location(modelName, configs)
    configs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(configs)
    return configs
def loadJsonConfig(configs):
    import json
    with open(configs) as f:
        return json.load(f)
    return None

def toAbsolutePath(path):    
    return os.path.abspath(path)

def initArgs(config, configType="json"):
    parser = argparse.ArgumentParser()
    if type(config) == str:
        if(configType == "json"):
            config = loadJsonConfig(config)
            addDict2Argparser(parser, config["args"])
        else:
            config = loadPyConfig(config)
            addDict2Argparser(parser, config.args)
    
    return parser.parse_args()