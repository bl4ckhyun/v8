// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Flags: --allow-natives-syntax

// Regression test: adding named properties to a dictionary-properties object
// should throw RangeError when the NameDictionary capacity limit is
// exceeded, not crash with a fatal "invalid table size" OOM.

function TestDictionaryPropertiesOverflow() {
  let obj = {};
  %OptimizeObjectForAddingMultipleProperties(obj, 0);
  assertFalse(%HasFastProperties(obj));

  for (let i = 0; ; i++) {
    obj['p' + i] = i;
  }
}

assertThrows(TestDictionaryPropertiesOverflow, RangeError,
             /Too many properties/);
