#!/usr/bin/env python3
#
# This file is part of Script of Scripts (SoS), a workflow system
# for the execution of commands and scripts in different languages.
# Please visit https://github.com/bpeng2000/SOS for more information.
#
# Copyright (C) 2016 Bo Peng (bpeng@mdanderson.org)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#


import os
import time
import shutil
import unittest
from io import StringIO

from sos.sos_script import SoS_Script
from sos.utils import env
from sos.sos_executor import Base_Executor, MP_Executor
from sos.target import FileTarget


class TestDAG(unittest.TestCase):
    def setUp(self):
        env.reset()
        self.temp_files = []

    def tearDown(self):
        for f in self.temp_files:
            FileTarget(f).remove('both')

    def touch(self, files):
        '''create temporary files'''
        if isinstance(files, str):
            files = [files]
        #
        for f in files:
            with open(f, 'w') as tmp:
                tmp.write('test')
        #
        self.temp_files.extend(files)

    def assertDAG(self, dag, content):
        out = StringIO()
        dag.write_dot(out)
        dot = out.getvalue()
        self.assertEqual(sorted([x.strip() for x in dot.split('\n') if x.strip()]),
            sorted([x.strip() for x in content.split('\n') if x.strip()]))

    def testSimpleDAG(self):
        '''Test DAG with simple dependency'''
        for filename in ('a.txt', 'a1.txt'):
            with open(filename, 'w') as tmp:
                tmp.write('hey')
        # basica case
        # 1 -> 2 -> 3 -> 4
        script = SoS_Script('''
[A_1]

[A_2]

[A_3]

[A_4]
        ''')
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''strict digraph "" {
A_2;
A_4;
A_1;
A_3;
A_2 -> A_3;
A_1 -> A_2;
A_3 -> A_4;
}
''')
        # basica case
        # 1 -> 2 -> 3 -> 4
        script = SoS_Script('''
[A_1]

[A_2]

[A_3]
input: 'a.txt'

[A_4]

        ''')
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''strict digraph "" {
A_2;
A_4;
A_1;
A_3;
A_1 -> A_2;
A_3 -> A_4;
}
''')


        #
        # 1 -> 2 -> 3 -> 4
        #
        script = SoS_Script('''
[A_1]
input: 'a.txt'
output: 'b.txt'

[A_2]
input: 'b.txt'
output: 'c.txt'

[A_3]
input: 'c.txt'
output: 'd.txt'

[A_4]
input: 'd.txt'
output: 'e.txt'

        ''')
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''strict digraph "" {
A_2;
A_4;
A_1;
A_3;
A_2 -> A_3;
A_1 -> A_2;
A_3 -> A_4;
}
''')
        #
        # 1 -> 2
        # 3 -> 4 (3 does not have any input)
        #
        script = SoS_Script('''
[B_1]
input: 'a.txt'
output: 'b.txt'

[B_2]
input: 'b.txt'
output: 'c.txt'

[B_3]
input: []
output: 'd.txt'

[B_4]
input: 'd.txt'
output: 'e.txt'

        ''')
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''strict digraph "" {
B_2;
B_4;
B_1;
B_3;
B_1 -> B_2;
B_3 -> B_4;
}
''')
        #
        # 1 -> 2
        # 3 -> 4 (3 depends on something else)
        #
        script = SoS_Script('''
[B_1]
input: 'a.txt'
output: 'b.txt'

[B_2]
input: 'b.txt'
output: 'c.txt'

[B_3]
input: 'a1.txt'
output: 'd.txt'

[B_4]
input: 'd.txt'
output: 'e.txt'

        ''')

        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''strict digraph "" {
B_1;
B_4;
B_2;
B_3;
B_1 -> B_2;
B_3 -> B_4;
}
''')
        #
        # (1) -> 2
        # (1) -> 3 -> 4
        #
        # 2 and 3 depends on the output of 1
        script = SoS_Script('''
[C_1]
input: 'a.txt'
output: 'b.txt'

[C_2]
input: 'b.txt'
output: 'c.txt'

[C_3]
input:  'b.txt'
output: 'd.txt'

[C_4]
depends: 'd.txt'
output: 'e.txt'

        ''')
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''
strict digraph "" {
C_1;
C_4;
C_2;
C_3;
C_1 -> C_2;
C_1 -> C_3;
C_3 -> C_4;
}
''')
        for filename in ('a.txt', 'a1.txt'):
            os.remove(filename)

    def testUndetermined(self):
        '''Test DAG with undetermined input.'''
        #
        for filename in ('a.txt', 'd.txt'):
            with open(filename, 'w') as tmp:
                tmp.write('hey')
        # input of step 3 is undertermined so
        # it depends on all its previous steps.
        script = SoS_Script('''
[C_1]
input: 'a.txt'
output: 'b.txt'

[C_2]
input: 'b.txt'
output: 'c.txt'

[C_3]
input:  dynamic('*.txt')
output: 'd.txt'

[C_4]
depends: 'd.txt'
output: 'e.txt'

        ''')
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        dag.show_nodes()
        #dag.write_dot('a.dot')
        self.assertDAG(dag,
'''
strict digraph "" {
C_1;
C_4;
C_2;
C_3;
C_1 -> C_2;
C_2 -> C_3;
C_3 -> C_4;
}
''')
        #
        # output of step
        #
        script = SoS_Script('''
[C_1]
input: 'a.txt'
output: 'b.txt'

[C_2]
input: 'b.txt'
output: 'c.txt'

[C_3]
input:  dynamic('*.txt')

[C_4]
depends: 'd.txt'
output: 'e.txt'

        ''')
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''
strict digraph "" {
C_1;
C_4;
C_2;
C_3;
C_1 -> C_2;
C_2 -> C_3;
C_3 -> C_4;
}
''')
        for filename in ('a.txt', 'd.txt'):
            os.remove(filename)

    def testAuxiliarySteps(self):
        script = SoS_Script('''
[K: provides='{name}.txt']
output: "${name}.txt"

sh:
    touch '${name}.txt'

[C_2]
input: 'b.txt'
output: 'c.txt'

sh:
    touch c.txt

[C_3]
input: 'a.txt'

        ''')
        # a.txt exists and b.txt does not exist
        with open('a.txt', 'w') as atfile:
            atfile.write('garbage')
        if os.path.isfile('b.txt'):
            os.remove('b.txt')
        # the workflow should call step K for step C_2, but not C_3
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        #dag.write_dot('a.dot')
        #dag.show_nodes()
        self.assertDAG(dag,
'''
strict digraph "" {
"K ['b.txt']";
C_3;
C_2;
"K ['b.txt']" -> C_2;
}
''')

    def testCycle(self):
        '''Test cycle detection of DAG'''
        #
        #  A.txt --> B.txt
        #
        #  B.txt --> C.txt
        #
        #  C.txt --> A.txt
        #
        script = SoS_Script('''
[A_1]
input: 'A.txt'
output: 'B.txt'

[A_2]
output: 'C.txt'

[A_3]
output: 'A.txt'
        ''')
        # the workflow should call step K for step C_2, but not C_3
        wf = script.workflow()
        self.assertRaises(RuntimeError, Base_Executor(wf).initialize_dag)

    def testLongChain(self):
        '''Test long make file style dependencies.'''
        #
        for f in ['A1.txt', 'A2.txt', 'C2.txt', 'B2.txt', 'B1.txt', 'B3.txt', 'C1.txt', 'C3.txt', 'C4.txt']:
            FileTarget(f).remove('both')
        #
        #  A1 <- B1 <- B2 <- B3
        #   |
        #   |
        #  \/
        #  A2 <- B2 <- C1 <- C2 <- C4
        #                    C3
        #
        script = SoS_Script('''
[A_1]
input: 'B1.txt'
output: 'A1.txt'
sh:
    touch A1.txt

[A_2]
depends:  'B2.txt'
sh:
    touch A2.txt

[B1: provides='B1.txt']
depends: 'B2.txt'
sh:
    touch B1.txt

[B2: provides='B2.txt']
depends: 'B3.txt', 'C1.txt'
sh:
    touch B2.txt

[B3: provides='B3.txt']
sh:
    touch B3.txt

[C1: provides='C1.txt']
depends: 'C2.txt', 'C3.txt'
sh:
    touch C1.txt

[C2: provides='C2.txt']
depends: 'C4.txt'
sh:
    touch C2.txt

[C3: provides='C3.txt']
depends: 'C4.txt'
sh:
    touch C3.txt

[C4: provides='C4.txt']
sh:
    touch C4.txt

        ''')
        # the workflow should call step K for step C_2, but not C_3
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''
strict digraph "" {
"C4 ['C4.txt']";
"B1 ['B1.txt']";
"C1 ['C1.txt']";
"C2 ['C2.txt']";
"C3 ['C3.txt']";
A_1;
"B2 ['B2.txt']";
"B3 ['B3.txt']";
A_2;
"C4 ['C4.txt']" -> "C2 ['C2.txt']";
"C4 ['C4.txt']" -> "C3 ['C3.txt']";
"B1 ['B1.txt']" -> A_1;
"C1 ['C1.txt']" -> "B2 ['B2.txt']";
"C2 ['C2.txt']" -> "C1 ['C1.txt']";
"C3 ['C3.txt']" -> "C1 ['C1.txt']";
A_1 -> A_2;
"B2 ['B2.txt']" -> "B1 ['B1.txt']";
"B2 ['B2.txt']" -> A_2;
"B3 ['B3.txt']" -> "B2 ['B2.txt']";
}
''')
        Base_Executor(wf).run()
        for f in ['A1.txt', 'A2.txt', 'C2.txt', 'B2.txt', 'B1.txt', 'B3.txt', 'C1.txt', 'C3.txt', 'C4.txt']:
            t = FileTarget(f)
            self.assertTrue(t.exists())
            t.remove('both')

    def testTarget(self):
        '''Test executing only part of a workflow.'''
        #
        for f in ['A1.txt', 'A2.txt', 'C2.txt', 'B2.txt', 'B1.txt', 'B3.txt', 'C1.txt', 'C3.txt', 'C4.txt']:
            FileTarget(f).remove('both')
        #
        #  A1 <- B1 <- B2 <- B3
        #   |
        #   |
        #  \/
        #  A2 <- B2 <- C1 <- C2 <- C4
        #                    C3
        #
        script = SoS_Script('''
[A_1]
input: 'B1.txt'
output: 'A1.txt'
sh:
    touch A1.txt

[A_2]
depends:  'B2.txt'
sh:
    touch A2.txt

[B1: provides='B1.txt']
depends: 'B2.txt'
sh:
    touch B1.txt

[B2: provides='B2.txt']
depends: 'B3.txt', 'C1.txt'
sh:
    touch B2.txt

[B3: provides='B3.txt']
sh:
    touch B3.txt

[C1: provides='C1.txt']
depends: 'C2.txt', 'C3.txt'
sh:
    touch C1.txt

[C2: provides='C2.txt']
depends: 'C4.txt'
sh:
    touch C2.txt

[C3: provides='C3.txt']
depends: 'C4.txt'
sh:
    touch C3.txt

[C4: provides='C4.txt']
sh:
    touch C4.txt

        ''')
        # the workflow should call step K for step C_2, but not C_3
        wf = script.workflow()
        #
        # test 1, we only need to generate target 'B1.txt'
        dag = Base_Executor(wf).initialize_dag(targets=['B1.txt'])
        # note that A2 is no longer mentioned
        self.assertDAG(dag,
'''
strict digraph "" {
"B3 ['B3.txt']";
"C4 ['C4.txt']";
"C2 ['C2.txt']";
"C1 ['C1.txt']";
"B1 ['B1.txt']";
"B2 ['B2.txt']";
"C3 ['C3.txt']";
"B3 ['B3.txt']" -> "B2 ['B2.txt']";
"C4 ['C4.txt']" -> "C3 ['C3.txt']";
"C4 ['C4.txt']" -> "C2 ['C2.txt']";
"C2 ['C2.txt']" -> "C1 ['C1.txt']";
"C1 ['C1.txt']" -> "B2 ['B2.txt']";
"B2 ['B2.txt']" -> "B1 ['B1.txt']";
"C3 ['C3.txt']" -> "C1 ['C1.txt']";
}
''')
        Base_Executor(wf).run(targets=['B1.txt'])
        for f in ['A1.txt', 'A2.txt']:
            self.assertFalse(FileTarget(f).exists())
        for f in ['C2.txt', 'B2.txt', 'B1.txt', 'B3.txt', 'C1.txt', 'C3.txt', 'C4.txt']:
            t = FileTarget(f)
            self.assertTrue(t.exists())
            t.remove('both')
        #
        # test 2, we would like to generate two files
        dag = Base_Executor(wf).initialize_dag(targets=['B2.txt', 'C2.txt'])
        # note that A2 is no longer mentioned
        self.assertDAG(dag,
'''
strict digraph "" {
"C4 ['C4.txt']";
"B2 ['B2.txt']";
"C3 ['C3.txt']";
"B3 ['B3.txt']";
"C2 ['C2.txt']";
"C1 ['C1.txt']";
"C4 ['C4.txt']" -> "C2 ['C2.txt']";
"C4 ['C4.txt']" -> "C3 ['C3.txt']";
"C3 ['C3.txt']" -> "C1 ['C1.txt']";
"B3 ['B3.txt']" -> "B2 ['B2.txt']";
"C2 ['C2.txt']" -> "C1 ['C1.txt']";
"C1 ['C1.txt']" -> "B2 ['B2.txt']";
}
''')
        Base_Executor(wf).run(targets=['B2.txt', 'C2.txt'])
        for f in ['A1.txt', 'B1.txt', 'A2.txt']:
            self.assertFalse(FileTarget(f).exists())
        for f in ['C2.txt', 'B2.txt', 'B3.txt', 'C1.txt', 'C3.txt', 'C4.txt']:
            t = FileTarget(f)
            self.assertTrue(t.exists())
            t.remove('both')
        #
        # test 3, generate two separate trees
        #
        dag = Base_Executor(wf).initialize_dag(targets=['B3.txt', 'C2.txt'])
        # note that A2 is no longer mentioned
        self.assertDAG(dag,
'''
strict digraph "" {
"B3 ['B3.txt']";
"C2 ['C2.txt']";
"C4 ['C4.txt']";
"C4 ['C4.txt']" -> "C2 ['C2.txt']";
}
''')
        Base_Executor(wf).run(targets=['B3.txt', 'C2.txt'])
        for f in ['A1.txt', 'B1.txt', 'A2.txt', 'B2.txt', 'C1.txt', 'C3.txt']:
            self.assertFalse(FileTarget(f).exists())
        for f in ['C2.txt', 'B3.txt', 'C4.txt']:
            t = FileTarget(f)
            self.assertTrue(t.exists())
            t.remove('both')

    def testPatternReuse(self):
        '''Test repeated use of steps that use pattern and produce different files.'''
        #
        for f in ['A1.txt', 'A2.txt', 'B1.txt', 'B1.txt.p', 'B2.txt', 'B2.txt.p']:
            FileTarget(f).remove('both')
        #
        #  A1 <- P <- B1
        #  A1 <- P <- B2
        #  A2
        #
        script = SoS_Script('''
[A_1]
input: 'B1.txt.p', 'B2.txt.p'
output: 'A1.txt'
sh:
    touch A1.txt

[A_2]
sh:
    touch A2.txt

[B1: provides='B1.txt']
sh:
    touch B1.txt

[B2: provides='B2.txt']
sh:
    touch B2.txt

[P: provides='{filename}.p']
input: filename
sh:
    touch ${output}
''')
        # the workflow should call step K for step C_2, but not C_3
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''
strict digraph "" {
"P ['B2.txt.p']";
"B1 ['B1.txt']";
"B2 ['B2.txt']";
A_2;
A_1;
"P ['B1.txt.p']";
"P ['B2.txt.p']" -> A_1;
"B1 ['B1.txt']" -> "P ['B1.txt.p']";
"B2 ['B2.txt']" -> "P ['B2.txt.p']";
A_1 -> A_2;
"P ['B1.txt.p']" -> A_1;
}
''')
        Base_Executor(wf).run()
        for f in ['A1.txt', 'A2.txt', 'B1.txt', 'B1.txt.p', 'B2.txt', 'B2.txt.p']:
            t = FileTarget(f)
            self.assertTrue(t.exists())
            t.remove('both')


    def testParallelExecution(self):
        '''Test basic parallel execution'''
        '''
        A1 <- None
        A2 <- B2
        '''
        for f in ['A1.txt', 'B2.txt', 'A2.txt']:
            FileTarget(f).remove('both')
        script = SoS_Script('''
[A_1]
output: 'A1.txt'
sh:
    sleep 3
    touch A1.txt

[A_2]
input:  'B2.txt'
output: 'A2.txt'
sh:
    sleep 3
    touch A2.txt

[B: provides='B2.txt']
output: 'B2.txt'
sh:
    touch B2.txt


''')
        # the workflow should call step K for step C_2, but not C_3
        wf = script.workflow()
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''
strict digraph "" {
A_1;
A_2;
"B ['B2.txt']";
"B ['B2.txt']" -> A_2;
}
''')
        env.max_jobs = 4
        st = time.time()
        #env.verbosity = 4
        MP_Executor(wf).run()
        self.assertLess(time.time() - st, 4)
        for f in ['A1.txt', 'B2.txt', 'A2.txt']:
            FileTarget(f).remove('both')


    def testDynamicNestedWorkflow(self):
        #
        # Because we are not sure which workflows would be executed
        # until run time, the DAG should not contain nested workflow
        # until runtime.
        #
        for f in ['B0.txt', 'B0.txt.p', 'B1.txt', 'B1.txt.p', 'B2.txt', 'B2.txt.p']:
            FileTarget(f).remove('both')
        #
        #  A1 <- P <- B
        #  A1 <- P <- B
        #  A2
        #
        #  ALL calls A and B with parameter
        #
        script = SoS_Script('''
[A_1]
parameter: num = 2
input: "B${num}.txt.p"

[B: provides='B{num}.txt']
sh:
    touch 'B${num}.txt'

[P: provides='{filename}.p']
input: filename
sh:
    touch ${output}

[ALL]

for num in range(3):
    sos_run('A')


''')
        # the workflow should call step K for step C_2, but not C_3
        wf = script.workflow('ALL')
        Base_Executor(wf).run()
        for f in ['B0.txt', 'B0.txt.p', 'B1.txt', 'B1.txt.p', 'B2.txt', 'B2.txt.p']:
            self.assertTrue(FileTarget(f).exists())
            FileTarget(f).remove('both')

    def testSharedDependency(self):
        #
        # shared variable should introduce additional dependency
        #
        for f in ['A1.txt']:
            FileTarget(f).remove('both')
        #
        # A1 introduces a shared variable ss, A3 depends on ss but not A2
        #
        script = SoS_Script('''
[A_1: shared='ss']
ss = 'A1'

[A_2]
input: None

sh:
    sleep 3

[A_3]
input: None
import time
time.sleep(3)
with open("${ss}.txt", 'w') as tmp:
    tmp.write('test')

''')
        wf = script.workflow('A')
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''
strict digraph "" {
A_3;
A_1;
A_2;
A_1 -> A_3;
}
''')
        env.max_jobs = 3
        st = time.time()
        MP_Executor(wf).run()
        self.assertLess(time.time() - st, 5)
        for f in ['A1.txt']:
            self.assertTrue(FileTarget(f).exists())
            FileTarget(f).remove('both')


    def testLiteralConnection(self):
        '''Testing the connection of steps with by variables.'''
        for f in ['A1.txt']:
            FileTarget(f).remove('both')
        #
        # A1 introduces a shared variable ss, A3 depends on ss but not A2
        #
        script = SoS_Script('''
[A_1: shared='p']
sh:
    touch 'A1.txt'

p = 'A1.txt'

[A_2]
input: None

sh:
    sleep 3

[A_3]
input: p

sh:
    sleep 3

[A_4]
input: p
sh:
    sleep 3

[A_5]
input: dynamic(p)
''')
        wf = script.workflow('A')
        dag = Base_Executor(wf).initialize_dag()
        self.assertDAG(dag,
'''
strict digraph "" {
A_1;
A_4;
A_2;
A_3;
A_5;
A_1 -> A_4;
A_1 -> A_3;
A_1 -> A_5;
A_4 -> A_5;
}
''')
        env.max_jobs = 3
        st = time.time()
        MP_Executor(wf).run()
        self.assertLess(time.time() - st, 5)
        for f in ['A1.txt']:
            self.assertTrue(FileTarget(f).exists())
            FileTarget(f).remove('both')


    def testVariableTarget(self):
        '''Test dependency caused by variable usage.'''
        script = SoS_Script(r'''
[A: shared='b']
b = 1

[C: shared={'c':'k'}]
k = 2

[all: shared='p']
depends: sos_variable('c'), sos_variable('b')

p = c + b

''')
        wf = script.workflow('all')
        Base_Executor(wf).run()
        self.assertTrue(env.sos_dict['p'], 3)


    def testReverseSharedVariable(self):
        '''Test shared variables defined in auxiliary steps'''
        FileTarget('a.txt').remove('both')
        script = SoS_Script(r'''
[A: shared='b', provides='a.txt']
b = 1
sh:
    touch a.txt

[B_1]
depends: 'a.txt'

[B_2]
print(b)

''')
        wf = script.workflow('B')
        Base_Executor(wf).run()
        self.assertTrue(env.sos_dict['b'], 1)

    def testChainedDepends(self):
        '''Test chain dependent'''
        shutil.rmtree('.sos')
        os.makedirs('.sos/.runtime')
        script = SoS_Script(r'''
# this step provides variable `var`
[index: provides='{filename}.bam.bai']
input: "${filename}.bam"
sh:
   echo "Generating ${output}"
   touch ${output}

[call: provides='{filename}.vcf']
input:   "${filename}.bam"
depends: "${input}.bai"
sh:
   echo "Calling variants from ${input} with ${depends} to ${output}"
   touch ${output}
''')
        FileTarget('a.bam.bai').remove('both')
        FileTarget('a.vcf').remove('both')
        self.touch('a.bam')
        Base_Executor(script.workflow()).run(targets=['a.vcf'])
        for file in ('a.vcf', 'a.bam', 'a.bam.bai'):
            FileTarget(file).remove('both')

if __name__ == '__main__':
    unittest.main()
