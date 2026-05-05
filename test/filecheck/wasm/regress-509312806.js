// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Flags: --fuzzing --allow-natives-syntax --sandbox-testing

function f(x) {
  let y = x;
  %WasmArray();
}
let info = %GetBytecode(f);
let bytes = new Uint8Array(info.bytecode);
for (let i = 0; i < bytes.length - 2; i++) {
  if (bytes[i] == 0x70 && bytes[i+1] == 0xa1 && bytes[i+2] == 0x02) {
    idx = i;
  }
}
bytes[idx+1] = 0xaf; // WasmTraceMemory
bytes[idx+4] = 0x01; // count = 1
%InstallBytecode(f, info);
f(0);
// CHECK: # The following harmless error was encountered
// CHECK-NOT: Did not crash.
print("Did not crash.")
