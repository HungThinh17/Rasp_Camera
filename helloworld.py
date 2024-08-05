import debugpy

debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()
debugpy.breakpoint()
print("Debugger is attached!")

print("hello world")