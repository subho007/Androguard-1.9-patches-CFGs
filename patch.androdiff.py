--- androguard-1.9/androdiff.py	2012-12-05 18:41:47.000000000 +0100
+++ androdiff_r1.py	2012-12-23 02:52:32.000000000 +0100
@@ -18,13 +18,14 @@
 # You should have received a copy of the GNU Lesser General Public License
 # along with Androguard.  If not, see <http://www.gnu.org/licenses/>.
 
-import sys
+import sys, os
 
 from optparse import OptionParser
 
 from androguard.core.bytecodes import apk, dvm
 from androguard.core.analysis import analysis
 from androguard.core import androconf
+from androguard.core.bytecode import diff2dot, diff2format
 
 sys.path.append("./elsim")
 from elsim import elsim
@@ -40,9 +41,25 @@
 #option_4 = { 'name' : ('-e', '--exclude'), 'help' : 'exclude specific blocks (0 : orig, 1 : diff, 2 : new)', 'nargs' : 1 }
 option_5 = { 'name' : ('-e', '--exclude'), 'help' : 'exclude specific class name (python regexp)', 'nargs' : 1 }
 option_6 = { 'name' : ('-s', '--size'), 'help' : 'exclude specific method below the specific size', 'nargs' : 1 }
-option_7 = { 'name' : ('-v', '--version'), 'help' : 'version of the API', 'action' : 'count' }
+option_7 = { 'name' : ('-g', '--graph'), 'help' : 'base directory to write generated graph of similarities', 'nargs' : 1 }
+option_8 = { 'name' : ('-v', '--version'), 'help' : 'version of the API', 'action' : 'count' }
 
-options = [option_0, option_1, option_2, option_3, option_5, option_6, option_7]
+options = [option_0, option_1, option_2, option_3, option_5, option_6, option_7, option_8]
+
+def valid_class_name( class_name ):
+    if class_name[-1] == ";" :
+        return class_name[1:-1]
+    return class_name
+
+def create_directory( class_name, output ) :
+    output_name = output
+    if output_name[-1] != "/" :
+        output_name = output_name + "/"
+
+    try :
+        os.makedirs( output_name + class_name )
+    except OSError :
+        pass
 
 def main(options, arguments) :
     details = False
@@ -92,6 +109,26 @@
 
             ddm = DiffDalvikMethod( i, j, elb, eld )
             ddm.show()
+            
+            if options.graph != None:
+                create_directory( valid_class_name( ddm.m1.m.get_class_name() ), options.graph )
+
+                if options.graph[-1] != "/" :
+                    options.graph = options.graph + "/"
+
+                filename1 = valid_class_name( ddm.m1.m.get_class_name() )
+                if filename1[-1] != "/" :
+                    filename1 = filename1 + "/"
+                    
+                descriptor1 = ddm.m1.m.get_descriptor()
+                descriptor1 = descriptor1.replace(";", "").replace(" ", "").replace("(", "-").replace(")", "-").replace("/", "_")
+                descriptor2 = ddm.m2.m.get_descriptor()
+                descriptor2 = descriptor2.replace(";", "").replace(" ", "").replace("(", "-").replace(")", "-").replace("/", "_")
+
+                filename = options.graph + filename1 + ddm.m1.m.get_name() + descriptor1 + "_vs_" + ddm.m2.m.get_name() + descriptor2
+                ms = diff2dot(ddm)
+                diff2format(filename +'.png','png', data = ms)
+
 
         print "NEW METHODS"
         enew = el.get_new_elements()
