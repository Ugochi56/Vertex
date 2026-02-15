import unittest
import os
import sys
import subprocess

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from vertex.cli import main as vertex_main

class TestIntegration(unittest.TestCase):
    def test_examples(self):
        # Locate examples directory relative to this test file
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        examples_dir = os.path.join(base_dir, 'examples')

        if not os.path.exists(examples_dir):
            print(f"Examples directory not found at {examples_dir}")
            return

        for filename in os.listdir(examples_dir):
            if filename.endswith('.vx'):
                filepath = os.path.join(examples_dir, filename)
                print(f"Testing {filename}...")

                # output file
                outfile = filepath.replace('.vx', '_gen.py')

                # Compile
                try:
                    # vertex_main expects argv list
                    ret = vertex_main(['vertex', filepath, '-o', outfile])
                    if ret != 0:
                        self.fail(f"Compilation failed for {filename} with return code {ret}")
                except SystemExit as e:
                    if e.code != 0:
                         self.fail(f"Compilation exited with error for {filename}")
                except Exception as e:
                    self.fail(f"Compilation raised exception for {filename}: {e}")

                # Run generated code
                try:
                    subprocess.check_call([sys.executable, outfile], stdout=subprocess.DEVNULL)
                except subprocess.CalledProcessError as e:
                    self.fail(f"Execution failed for {filename}: {e}")
                finally:
                    # cleanup
                    if os.path.exists(outfile):
                        os.remove(outfile)

if __name__ == '__main__':
    unittest.main()
