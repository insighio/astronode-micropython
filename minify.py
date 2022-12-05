import python_minifier

with open("./astronode.py") as f:
    contents = python_minifier.minify(f.read(),
                                        remove_annotations=True,
                                        remove_pass=False,
                                        remove_literal_statements=True,
                                        combine_imports=True,
                                        hoist_literals=True,
                                        rename_locals=True,
                                        preserve_locals=None,
                                        rename_globals=False,
                                        preserve_globals=None,
                                        remove_object_base=False,
                                        convert_posargs_to_args=False,
                                        preserve_shebang=True)
with open("./astronode.min.py","w") as fp:
     fp.writelines(contents)
