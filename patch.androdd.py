--- androguard-1.9/androdd.py	2012-12-05 18:41:47.000000000 +0100
+++ androdd_r1.py	2012-12-23 03:29:44.000000000 +0100
@@ -35,7 +35,9 @@
 
 option_4 = { 'name' : ('-v', '--version'), 'help' : 'version of the API', 'action' : 'count' }
 
-options = [option_0, option_1, option_2, option_3, option_4]
+option_5 = { 'name' : ('-l', '--limit'), 'help' : 'Limit analysis to specific method', 'nargs' : 1}
+
+options = [option_0, option_1, option_2, option_3, option_4, option_5]
 
 def valid_class_name( class_name ):
     if class_name[-1] == ";" :
@@ -52,12 +54,7 @@
     except OSError :
         pass
 
-def create_directories( a, output ) :
-    for vm in a.get_vms() :
-        for class_name in vm.get_classes_names() :
-            create_directory( valid_class_name( class_name ), output )
-
-def export_apps_to_format( a, output, dot=None, _format=None ) :
+def export_apps_to_format( a, output, lmethod_name=None, dot=None, _format=None ) :
     output_name = output
     if output_name[-1] != "/" :
         output_name = output_name + "/"
@@ -65,6 +62,16 @@
     for vm in a.get_vms() :
         x = analysis.VMAnalysis( vm )
         for method in vm.get_methods() :
+            if lmethod_name != None :            
+                if len(lmethod_name.split(';')) > 1 :
+                    msig = "%s%s%s" % (method.get_class_name(),method.get_name(), method.get_descriptor())                    
+                else :
+                    msig = "%s" % (method.get_class_name()[:-1])
+                if msig != lmethod_name :
+                    continue
+            
+            create_directory( valid_class_name( method.get_class_name() ), output )
+
             filename = output_name + valid_class_name( method.get_class_name() )
             if filename[-1] != "/" :
                 filename = filename + "/"
@@ -94,16 +101,15 @@
         a = Androguard( [ options.input ] )
 
         if options.dot != None or options.format != None :
-            create_directories( a, options.output )
-            export_apps_to_format( a, options.output, options.dot, options.format )
+            export_apps_to_format( a, options.output, options.limit, options.dot, options.format)
         else :
-          print "Please, specify a format or dot option"
+            print "Please, specify a format or dot option"
 
     elif options.version != None :
         print "Androdd version %s" % androconf.ANDROGUARD_VERSION
     
     else :
-      print "Please, specify an input file and an output directory"
+        print "Please, specify an input file and an output directory"
 
 if __name__ == "__main__" :
     parser = OptionParser()
