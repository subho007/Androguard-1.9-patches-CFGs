--- androguard-1.9/androguard/core/bytecode.py	2012-12-05 18:41:47.000000000 +0100
+++ bytecode_r1.py	2012-12-23 03:10:25.000000000 +0100
@@ -18,6 +18,9 @@
 
 from struct import unpack, pack
 
+import hashlib
+from xml.sax.saxutils import escape
+
 from androconf import Color, warning, error, CONF, disable_colors, enable_colors, remove_colors, save_colors
 
 def disable_print_colors() :
@@ -205,6 +208,145 @@
     if d :
         getattr(d, "write_" + _format)( output )
       
+def diff2dot( ddm ):
+    """
+        Export analysis (two methods similarities) to dot format with HTML-Like Labels
+            - graphviz > 1.10
+
+        @param ddm : DiffDalvikMethod object
+
+        @rtype : subgraphs dicts list
+    """
+
+    r = { 'subgraphs' : [] }
+
+    # dot format HTML-Like based strings
+    node_tpl  = "\nstruct_%s [label=<\n<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"3\">\n%s</TABLE>>];\n"
+    label_tpl = "<TR><TD ALIGN=\"LEFT\" BGCOLOR=\"%s\"> %x %s </TD></TR>\n"
+    link_tpl = "<TR><TD PORT=\"%s\"></TD></TR>\n"
+
+    methods = [ddm.m1, ddm.m2]
+    edges_html  = ""
+    
+    # loop over ddm methods (m1 and m2)    
+    for method in methods:
+        vm = method.mx.get_vm()
+        blocks_html = ""
+
+        # loop over method blocks
+        for DVMBasicMethodBlock in method.mx.basic_blocks.gets():
+            ins_idx = DVMBasicMethodBlock.start
+            block_id = hashlib.md5(method.sha256+DVMBasicMethodBlock.method.class_name+DVMBasicMethodBlock.method.name+DVMBasicMethodBlock.name).hexdigest()
+            content = link_tpl % 'header'
+            
+            # loop over method instructions
+            for DVMBasicMethodBlockInstruction in DVMBasicMethodBlock.get_instructions():
+                instruction_located = False
+
+                for LinkedBlock in ddm.eld.filters[ 'link elements' ]:
+                    alterLinkedBlock = ddm.eld.filters[ 'link elements' ][ LinkedBlock ]
+
+                    # instruction to be deleted or added
+                    if instruction_located == False:        
+                                    
+                        sameclass = (DVMBasicMethodBlock.method.class_name == LinkedBlock.bb.method.class_name)
+                        samemethod = (DVMBasicMethodBlock.method.name == LinkedBlock.bb.method.name)
+                        sameblock = (DVMBasicMethodBlock.name == LinkedBlock.bb.name)
+                        # the instruction is tagged as new instruction ?
+                        if (sameclass and samemethod and sameblock):
+
+                            # loop over added elements
+                            for AddedInstruction in ddm.eld.filters[ 'added elements' ][ LinkedBlock ]:
+                                sameinstruction = (DVMBasicMethodBlockInstruction.get_raw() == AddedInstruction.ins.get_raw())
+                                sameoffset      = (ins_idx == (AddedInstruction.bb.bb.start + AddedInstruction.offset))
+                                
+                                # "to add" instruction equal to method instruction
+                                if (sameinstruction and sameoffset):
+                                    content += label_tpl % ('GREEN', ins_idx, escape(vm.dotbuff(DVMBasicMethodBlockInstruction, ins_idx)) )
+                                    instruction_located = True
+                                    break
+
+                        sameclass = (DVMBasicMethodBlock.method.class_name == alterLinkedBlock.bb.method.class_name)
+                        samemethod = (DVMBasicMethodBlock.method.name == alterLinkedBlock.bb.method.name)
+                        sameblock = (DVMBasicMethodBlock.name == alterLinkedBlock.bb.name)
+                        # the instruction is tagged as deleted instruction ?
+                        if (sameclass and samemethod and sameblock):
+                        
+                            # loop over deleted elements
+                            for DeletedInstruction in ddm.eld.filters[ 'deleted elements' ][ alterLinkedBlock ] :
+                                # deleted instruction equal to method instruction
+                                sameinstruction = (DVMBasicMethodBlockInstruction.get_raw() == DeletedInstruction.ins.get_raw())
+                                sameoffset      = (ins_idx == (DeletedInstruction.bb.bb.start + DeletedInstruction.offset))
+
+                                # "to delete" instruction equal to method instruction
+                                if (sameinstruction and sameoffset):
+                                    content += label_tpl % ('RED', ins_idx, escape(vm.dotbuff(DVMBasicMethodBlockInstruction, ins_idx)) )
+                                    instruction_located = True
+                                    break
+
+                # not deleted nor added, so unchanged instruction 
+                if not instruction_located:
+                    content += label_tpl % ('LIGHTGRAY', ins_idx, escape(vm.dotbuff(DVMBasicMethodBlockInstruction, ins_idx)) )
+
+                ins_idx += DVMBasicMethodBlockInstruction.get_length()
+
+            # all blocks from one method parsed
+            # updating dot HTML content
+            content += link_tpl % 'tail'
+            blocks_html += node_tpl % (block_id, content)
+
+            # Block edges color treatment (conditional branchs colors)
+            val = "green"
+            if len(DVMBasicMethodBlock.childs) > 1 :
+                val = "red"
+            elif len(DVMBasicMethodBlock.childs) == 1 :
+                val = "blue"
+
+            # updating dot edges
+            for DVMBasicMethodBlockChild in DVMBasicMethodBlock.childs:
+                child_id = hashlib.md5(method.sha256+DVMBasicMethodBlockChild[-1].method.class_name+DVMBasicMethodBlockChild[-1].method.name+DVMBasicMethodBlockChild[-1].name).hexdigest()
+                edges_html += "struct_%s:tail -> struct_%s:header  [color=\"%s\"];\n" % ( block_id, child_id ,val)
+                # color switch
+                if val == "red" :
+                    val = "green"
+
+        r['subgraphs'].append({ 'name': method.m.class_name+"."+method.m.name+"->"+method.m.get_descriptor(), 'nodes' : blocks_html, 'edges' : edges_html })        
+
+    return r      
+
+def diff2format( output, _format="png", data = False ) :
+    """
+        Export method to a specific file format
+
+        @param output : output filename
+        @param _format : format type (png, jpg ...) (default : png)
+        @param raw : subgraphs dicts list
+    """
+    try :
+        import pydot
+    except ImportError :
+        error("module pydot not found")
+
+    buff = "digraph {\n"
+    buff += "graph [ rankdir=TB]\n"
+    buff += "node [shape=plaintext]\n"
+
+    i=0
+    # subgraphs cluster
+    for subgraph in data['subgraphs']:
+        buff += "subgraph cluster_" + hashlib.md5(output).hexdigest() + str(i) + " {\nlabel=\"%s\"\n" % subgraph['name']
+        buff +=  subgraph['nodes']
+        buff += "}\n"
+        i+=1
+        
+    # subgraphs edges
+    buff += subgraph['edges']
+    buff += "}\n"
+
+    d = pydot.graph_from_dot_data( buff )
+    if d :
+        getattr(d, "write_" + _format)( output )
+
 def method2png( output, mx, raw = False ) :
     """
         Export method to a png file format
@@ -306,31 +448,14 @@
     def show(self, value) :
         getattr(self, "show_" + value)()
 
-
-class BuffHandle:
-    def __init__(self, buff):
+class BuffHandle :
+    def __init__(self, buff) :
         self.__buff = buff
         self.__idx = 0
 
-    def size(self):
-        return len(self.__buff)
-
-    def set_idx(self, idx):
-        self.__idx = idx
-
-    def get_idx(self):
-        return self.__idx
-
-    def readNullString(self, size):
-        data = self.read(size)
-        return data
-
     def read_b(self, size) :
         return self.__buff[ self.__idx : self.__idx + size ]
 
-    def read_at(self, offset, size):
-        return self.__buff[ offset : offset + size ]
-
     def read(self, size) :
         if isinstance(size, SV) :
             size = size.value
@@ -438,10 +563,4 @@
     i = i.replace(" ", "")
     i = i.replace("$", "")
 
-    return i
-
-class Node:
- def __init__(self, n, s):
-     self.id = n
-     self.title = s
-     self.children = []
\ No newline at end of file
+    return i
\ No newline at end of file
