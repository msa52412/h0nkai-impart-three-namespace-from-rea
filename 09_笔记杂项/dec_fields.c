// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x18042F810 ================= */
/* name   = FUN_18042f810 */
/* entry  = 18042f810 */
/* body   = 898 bytes */
/* sig    = undefined FUN_18042f810() */


undefined8
FUN_18042f810(longlong param_1,longlong param_2,char param_3,longlong param_4,ulonglong *param_5)

{
  byte bVar1;
  int iVar2;
  undefined4 *puVar3;
  char cVar4;
  longlong lVar5;
  longlong lVar6;
  longlong lVar7;
  undefined8 uVar8;
  undefined8 *puVar9;
  ulonglong uVar10;
  longlong local_28 [2];
  
  if (*(char *)(param_4 + 0x13f) == '\0') {
    return 0;
  }
  lVar5 = param_1 + -0x10;
  if (param_3 == '\0') {
    lVar5 = param_1;
  }
LAB_18042f84e:
  uVar10 = 0;
LAB_18042f864:
  if (uVar10 == 0) {
    FUN_18044b5c0(param_4);
    if (*(short *)(param_4 + 0x12a) == 0) goto LAB_18042fb6b;
    uVar10 = *(ulonglong *)(param_4 + 0x10);
  }
  else {
    uVar10 = uVar10 + 0x20;
    if ((ulonglong)*(ushort *)(param_4 + 0x12a) * 0x20 + *(longlong *)(param_4 + 0x10) <= uVar10)
    goto LAB_18042fb6b;
  }
  if (uVar10 == 0) goto LAB_18042fb6b;
  lVar7 = *(longlong *)(uVar10 + 0x10);
  if ((*(byte *)(lVar7 + -0x5a6601071b4f6182) & 0x10) == 0) {
    if ((*(uint *)(lVar7 + -0x5a6601071b4f6182) & 0x40000000) == 0) {
      if (((*(char *)(lVar7 + -0x5a6601071b4f6180) != '\x11') ||
          (lVar6 = FUN_18043b320(*(undefined4 *)(lVar7 + -0x5a6601071b4f618a)),
          *(char *)(lVar6 + 0x137) != '\0')) && (*(char *)(lVar7 + -0x5a6601071b4f6180) != '\x16'))
      {
        if ((*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x15') &&
           (lVar6 = FUN_18043b320(**(undefined4 **)(lVar7 + -0x5a6601071b4f618a)),
           *(char *)(lVar6 + 0x142) != '\0')) {
          puVar3 = *(undefined4 **)(lVar7 + -0x5a6601071b4f618a);
          lVar7 = FUN_18043b320(*puVar3);
          if ((*(char *)(lVar7 + 0x142) == '\0') ||
             (lVar7 = FUN_18043b320(*puVar3), *(char *)(lVar7 + 0x137) == '\0')) goto LAB_18042f9fe;
        }
        goto LAB_18042f978;
      }
    }
    else {
LAB_18042f978:
      lVar7 = *(longlong *)(uVar10 + 0x10);
      if (((((*(byte *)(lVar7 + -0x5a6601071b4f6182) & 0x40) != 0) ||
           (*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x0e')) ||
          ((undefined8 *)(lVar7 + -0x5a6601071b4f618a) == (undefined8 *)0x0)) ||
         (((bVar1 = *(byte *)(lVar7 + -0x5a6601071b4f6180), 0x1d < bVar1 ||
           ((0x30144000U >> ((int)(char)bVar1 & 0x1fU) & 1) == 0)) &&
          ((bVar1 != 0x15 ||
           (lVar7 = FUN_18043b320(**(undefined4 **)(lVar7 + -0x5a6601071b4f618a)),
           *(char *)(lVar7 + 0x142) != '\0')))))) goto LAB_18042f864;
    }
LAB_18042f9fe:
    lVar7 = *(longlong *)(uVar10 + 0x10);
    puVar9 = (undefined8 *)(lVar7 + -0x5a6601071b4f618a);
    if ((*(uint *)(lVar7 + -0x5a6601071b4f6182) & 0x40000000) == 0) {
      if (((*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x11') &&
          (lVar6 = FUN_18043b320(*(undefined4 *)puVar9), *(char *)(lVar6 + 0x137) == '\0')) ||
         (*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x16')) {
LAB_18042fa80:
        iVar2 = *(int *)(uVar10 + 0x1c);
        lVar7 = *(longlong *)(uVar10 + 0x10);
        if (*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x15') {
          uVar8 = *(undefined8 *)(*(longlong *)(lVar7 + -0x5a6601071b4f618a) + 0x18);
        }
        else {
          uVar8 = FUN_18043b320(*(undefined4 *)(lVar7 + -0x5a6601071b4f618a));
        }
        cVar4 = FUN_18042f810((iVar2 + -0x7f804675) + lVar5,param_2,1,uVar8,param_5);
        if (cVar4 != '\0') goto LAB_18042faf5;
        goto LAB_18042f864;
      }
      if ((*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x15') &&
         (lVar7 = FUN_18043b320(*(undefined4 *)*puVar9), *(char *)(lVar7 + 0x142) != '\0')) {
        puVar3 = (undefined4 *)*puVar9;
        lVar7 = FUN_18043b320(*puVar3);
        if ((*(char *)(lVar7 + 0x142) == '\0') ||
           (lVar7 = FUN_18043b320(*puVar3), *(char *)(lVar7 + 0x137) == '\0')) goto LAB_18042fa80;
      }
    }
    if (*(int *)(uVar10 + 0x1c) != 0x7f804674) {
      local_28[0] = 0;
      FUN_18044ae60(*(longlong *)(uVar10 + 0x10) + -0x5a6601071b4f618a,local_28,
                    (*(int *)(uVar10 + 0x1c) + -0x7f804675) + lVar5,1);
      if (local_28[0] == param_2) {
LAB_18042faf5:
        *param_5 = uVar10;
        return 1;
      }
    }
  }
  goto LAB_18042f864;
LAB_18042fb6b:
  param_4 = *(longlong *)(param_4 + 0x80);
  if (param_4 == 0) {
    return 0;
  }
  goto LAB_18042f84e;
}



/* ================= 0x18044DC30 ================= */
/* name   = FUN_18044dc30 */
/* entry  = 18044dc30 */
/* body   = 968 bytes */
/* sig    = undefined FUN_18044dc30() */


ulonglong FUN_18044dc30(longlong param_1,char param_2,longlong param_3,undefined8 param_4,
                       undefined4 param_5)

{
  byte bVar1;
  undefined4 *puVar2;
  byte bVar3;
  ulonglong in_RAX;
  longlong lVar4;
  longlong lVar5;
  longlong lVar6;
  undefined8 uVar7;
  undefined8 *puVar8;
  ulonglong uVar9;
  byte local_res18;
  undefined8 local_20;
  
  bVar3 = 0;
  local_res18 = 0;
  if (*(char *)(param_3 + 0x13f) == '\0') {
    return in_RAX & 0xffffffffffffff00;
  }
  lVar4 = param_1 + -0x10;
  if (param_2 == '\0') {
    lVar4 = param_1;
  }
LAB_18044dc83:
  uVar9 = 0;
LAB_18044dc95:
  if (uVar9 == 0) {
    FUN_18044b5c0(param_3);
    if (*(short *)(param_3 + 0x12a) == 0) goto LAB_18044dfc9;
    uVar9 = *(ulonglong *)(param_3 + 0x10);
  }
  else {
    uVar9 = uVar9 + 0x20;
    if ((ulonglong)*(ushort *)(param_3 + 0x12a) * 0x20 + *(longlong *)(param_3 + 0x10) <= uVar9)
    goto LAB_18044dfc9;
  }
  if (uVar9 == 0) goto LAB_18044dfc9;
  lVar6 = *(longlong *)(uVar9 + 0x10);
  bVar3 = local_res18;
  if ((*(byte *)(lVar6 + -0x5a6601071b4f6182) & 0x10) == 0) {
    if ((*(uint *)(lVar6 + -0x5a6601071b4f6182) & 0x40000000) == 0) {
      if (((*(char *)(lVar6 + -0x5a6601071b4f6180) != '\x11') ||
          (lVar5 = FUN_18043b320(*(undefined4 *)(lVar6 + -0x5a6601071b4f618a)),
          *(char *)(lVar5 + 0x137) != '\0')) && (*(char *)(lVar6 + -0x5a6601071b4f6180) != '\x16'))
      {
        if ((*(char *)(lVar6 + -0x5a6601071b4f6180) == '\x15') &&
           (lVar5 = FUN_18043b320(**(undefined4 **)(lVar6 + -0x5a6601071b4f618a)),
           *(char *)(lVar5 + 0x142) != '\0')) {
          puVar2 = *(undefined4 **)(lVar6 + -0x5a6601071b4f618a);
          lVar6 = FUN_18043b320(*puVar2);
          if ((*(char *)(lVar6 + 0x142) == '\0') ||
             (lVar6 = FUN_18043b320(*puVar2), *(char *)(lVar6 + 0x137) == '\0')) goto LAB_18044de39;
        }
        goto LAB_18044dda9;
      }
    }
    else {
LAB_18044dda9:
      lVar6 = *(longlong *)(uVar9 + 0x10);
      if (((((*(byte *)(lVar6 + -0x5a6601071b4f6182) & 0x40) != 0) ||
           (*(char *)(lVar6 + -0x5a6601071b4f6180) == '\x0e')) ||
          ((undefined8 *)(lVar6 + -0x5a6601071b4f618a) == (undefined8 *)0x0)) ||
         (((bVar1 = *(byte *)(lVar6 + -0x5a6601071b4f6180), 0x1d < bVar1 ||
           ((0x30144000U >> ((int)(char)bVar1 & 0x1fU) & 1) == 0)) &&
          ((bVar1 != 0x15 ||
           (lVar6 = FUN_18043b320(**(undefined4 **)(lVar6 + -0x5a6601071b4f618a)),
           *(char *)(lVar6 + 0x142) != '\0')))))) goto LAB_18044dc95;
    }
LAB_18044de39:
    lVar6 = *(longlong *)(uVar9 + 0x10);
    puVar8 = (undefined8 *)(lVar6 + -0x5a6601071b4f618a);
    if ((*(uint *)(lVar6 + -0x5a6601071b4f6182) & 0x40000000) == 0) {
      if (((*(char *)(lVar6 + -0x5a6601071b4f6180) != '\x11') ||
          (lVar5 = FUN_18043b320(*(undefined4 *)puVar8), *(char *)(lVar5 + 0x137) != '\0')) &&
         (*(char *)(lVar6 + -0x5a6601071b4f6180) != '\x16')) {
        if ((*(char *)(lVar6 + -0x5a6601071b4f6180) == '\x15') &&
           (lVar6 = FUN_18043b320(*(undefined4 *)*puVar8), *(char *)(lVar6 + 0x142) != '\0')) {
          puVar2 = (undefined4 *)*puVar8;
          lVar6 = FUN_18043b320(*puVar2);
          if ((*(char *)(lVar6 + 0x142) == '\0') ||
             (lVar6 = FUN_18043b320(*puVar2), *(char *)(lVar6 + 0x137) == '\0')) goto LAB_18044deb7;
        }
        goto LAB_18044df33;
      }
LAB_18044deb7:
      lVar6 = *(longlong *)(uVar9 + 0x10);
      lVar5 = (*(int *)(uVar9 + 0x1c) + -0x7f804675) + lVar4;
      if (*(char *)(lVar6 + -0x5a6601071b4f6180) == '\x15') {
        bVar3 = FUN_18044dc30(lVar5,1,*(undefined8 *)
                                       (*(longlong *)(lVar6 + -0x5a6601071b4f618a) + 0x18),param_4,
                              param_5);
      }
      else {
        uVar7 = FUN_18043b320(*(undefined4 *)(lVar6 + -0x5a6601071b4f618a));
        bVar3 = FUN_18044dc30(lVar5,1,uVar7,param_4,param_5);
      }
    }
    else {
LAB_18044df33:
      if (*(int *)(uVar9 + 0x1c) == 0x7f804674) goto LAB_18044dc95;
      local_20 = 0;
      FUN_18044ae60(*(longlong *)(uVar9 + 0x10) + -0x5a6601071b4f618a,&local_20,
                    (*(int *)(uVar9 + 0x1c) + -0x7f804675) + lVar4,1);
      bVar3 = FUN_18042bb40(local_20,param_4,param_5);
    }
    local_res18 = local_res18 | bVar3;
    bVar3 = local_res18;
  }
  goto LAB_18044dc95;
LAB_18044dfc9:
  param_3 = *(longlong *)(param_3 + 0x80);
  if (param_3 == 0) {
    return (ulonglong)bVar3;
  }
  goto LAB_18044dc83;
}



/* ================= 0x180443160 ================= */
/* name   = FUN_180443160 */
/* entry  = 180443160 */
/* body   = 2992 bytes */
/* sig    = undefined FUN_180443160() */


void FUN_180443160(longlong param_1)

{
  byte bVar1;
  uint uVar2;
  ulonglong uVar3;
  char cVar4;
  undefined4 uVar5;
  undefined8 *puVar6;
  longlong lVar7;
  undefined8 uVar8;
  longlong lVar9;
  char *pcVar10;
  undefined8 *puVar11;
  undefined8 *puVar12;
  undefined8 *puVar13;
  ushort uVar14;
  byte *pbVar15;
  ulonglong uVar16;
  undefined4 uVar17;
  longlong lVar18;
  ushort uVar19;
  bool bVar20;
  undefined8 *local_res8;
  undefined8 **local_138;
  undefined8 **ppuStack_130;
  undefined8 **local_128;
  undefined8 **local_120;
  undefined8 **ppuStack_118;
  undefined8 **local_110;
  undefined8 **local_108;
  undefined8 **ppuStack_100;
  undefined8 **local_f8;
  byte local_f0;
  undefined7 uStack_ef;
  undefined8 local_e0;
  ulonglong local_d8;
  longlong local_d0 [4];
  undefined4 local_b0;
  undefined1 local_a8;
  undefined1 local_a7;
  longlong local_a0;
  undefined4 local_98;
  longlong local_90 [3];
  undefined4 local_78;
  longlong local_60 [3];
  undefined4 local_48;
  undefined8 local_30;
  
  local_30 = 0xfffffffffffffffe;
  if (*(char *)(param_1 + 0x13e) == '\0') {
    lVar7 = *(longlong *)(param_1 + 0x80);
    if (lVar7 == 0) {
      uVar5 = 0x10;
      uVar17 = 0x10;
      *(undefined1 *)(param_1 + 0x133) = 8;
    }
    else {
      *(byte *)(param_1 + 0x13a) = *(byte *)(param_1 + 0x13a) | *(byte *)(lVar7 + 0x13a);
      uVar5 = *(undefined4 *)(lVar7 + 0x114);
      uVar17 = *(undefined4 *)(lVar7 + 0x11c);
      if (*(char *)(param_1 + 0x142) == '\0') {
        *(undefined1 *)(param_1 + 0x133) = *(undefined1 *)(lVar7 + 0x133);
      }
      else {
        *(undefined1 *)(param_1 + 0x133) = 1;
      }
    }
    if (*(short *)(param_1 + 0x12a) == 0) {
      FUN_18044ea30(param_1,uVar5);
      *(undefined4 *)(param_1 + 0x11c) = uVar17;
    }
    else {
      puVar13 = (undefined8 *)0x0;
      uVar14 = 0;
      bVar20 = *(short *)(param_1 + 0x12a) != 0;
      uVar19 = uVar14;
      while( true ) {
        if (!bVar20) break;
        lVar18 = (ulonglong)uVar19 * 0x20 + *(longlong *)(param_1 + 0x10);
        lVar7 = *(longlong *)(lVar18 + 0x10);
        if ((~(byte)(*(uint *)(lVar7 + -0x5a6601071b4f6182) >> 4) & 1) != 0) {
          puVar6 = (undefined8 *)FUN_18043bf90(lVar7 + -0x5a6601071b4f618a);
          bVar1 = *(byte *)((longlong)puVar6 + 10);
          if ((bVar1 != 0x15) || (bVar20 = true, *(int *)*puVar6 != -1)) {
            bVar20 = false;
          }
          if (bVar20) {
            local_d8 = 0xf;
            local_e0 = 0;
            local_f0 = 0;
            FUN_1803f8e30(&local_f0,"The field \'");
            pcVar10 = (char *)(*(ulonglong *)(lVar18 + 8) ^ 0x73ecc7d44725af21);
            puVar6 = puVar13;
            if (*pcVar10 != '\0') {
              puVar6 = (undefined8 *)0xffffffffffffffff;
              do {
                puVar6 = (undefined8 *)((longlong)puVar6 + 1);
              } while (pcVar10[(longlong)puVar6] != '\0');
            }
            FUN_1803f8e30(&local_f0,pcVar10,puVar6);
            FUN_1803f8e30(&local_f0,"\' in type \'",0xb);
            pcVar10 = *(char **)(param_1 + 0xa8);
            if (*pcVar10 != '\0') {
              puVar13 = (undefined8 *)0xffffffffffffffff;
              do {
                puVar13 = (undefined8 *)((longlong)puVar13 + 1);
              } while (pcVar10[(longlong)puVar13] != '\0');
            }
            FUN_1803f8e30(&local_f0,pcVar10,puVar13);
            FUN_1803f8e30(&local_f0,
                          "\' has a type which was not generated by il2cpp.exe. Consider using a generic type which is not nested so deeply."
                          ,0x70);
            *(undefined1 *)(param_1 + 0x13d) = 1;
            *(undefined1 *)(param_1 + 0x136) = 0;
            pbVar15 = &local_f0;
            if (0xf < local_d8) {
              pbVar15 = (byte *)CONCAT71(uStack_ef,local_f0);
            }
            uVar8 = FUN_1804303f0(DAT_1899db1c0,"System","ExecutionEngineException",pbVar15);
            uVar5 = FUN_1804fb600(uVar8,0);
            *(undefined4 *)(param_1 + 0xe0) = uVar5;
            if (local_d8 < 0x10) {
              return;
            }
            uVar3 = CONCAT71(uStack_ef,local_f0);
            uVar16 = uVar3;
            if (0xfff < local_d8 + 1) {
              if ((local_f0 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
                FUN_180509dc8();
              }
              uVar16 = *(ulonglong *)(uVar3 - 8);
              if (uVar3 <= uVar16) {
                    /* WARNING: Subroutine does not return */
                FUN_180509dc8();
              }
              if (uVar3 - uVar16 < 8) {
                    /* WARNING: Subroutine does not return */
                FUN_180509dc8();
              }
              if (0x27 < uVar3 - uVar16) {
                    /* WARNING: Subroutine does not return */
                FUN_180509dc8();
              }
            }
            thunk_FUN_18050a3b8(uVar16);
            return;
          }
          if (((bVar1 < 0x1e) && ((0x30144000U >> (bVar1 & 0x1f) & 1) != 0)) ||
             ((bVar1 == 0x15 &&
              (lVar7 = FUN_18043b320(*(undefined4 *)*puVar6), *(char *)(lVar7 + 0x142) == '\0')))) {
LAB_1804432bc:
            *(undefined1 *)(param_1 + 0x13a) = 1;
          }
          else {
            cVar4 = FUN_1804426f0(puVar6);
            if (cVar4 != '\0') {
              uVar8 = FUN_180430150(puVar6,1);
              cVar4 = FUN_18043d100(uVar8);
              if (cVar4 != '\0') goto LAB_1804432bc;
            }
          }
        }
        uVar19 = uVar19 + 1;
        bVar20 = uVar19 < *(ushort *)(param_1 + 0x12a);
      }
      local_120 = (undefined8 **)0x0;
      ppuStack_118 = (undefined8 **)0x0;
      local_110 = (undefined8 **)0x0;
      local_138 = (undefined8 **)0x0;
      ppuStack_130 = (undefined8 **)0x0;
      local_128 = (undefined8 **)0x0;
      local_108 = (undefined8 **)0x0;
      ppuStack_100 = (undefined8 **)0x0;
      local_f8 = (undefined8 **)0x0;
      uVar19 = uVar14;
      if (*(short *)(param_1 + 0x12a) != 0) {
        do {
          lVar18 = (ulonglong)uVar19 * 0x20 + *(longlong *)(param_1 + 0x10);
          lVar7 = *(longlong *)(lVar18 + 0x10);
          puVar6 = (undefined8 *)(lVar7 + -0x5a6601071b4f618a);
          if (((*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x11') &&
              (lVar9 = FUN_18043b320(*(undefined4 *)puVar6), *(char *)(lVar9 + 0x137) != '\0')) &&
             ((*(uint *)(lVar7 + -0x5a6601071b4f6182) & 0x40000000) == 0)) {
            lVar9 = FUN_18043b320(*(undefined4 *)puVar6);
LAB_1804434e2:
            puVar6 = puVar13;
            if (*(longlong *)(lVar9 + 0x30) != lVar9) {
              puVar6 = (undefined8 *)(*(longlong *)(lVar9 + 0x30) + 0x60);
            }
          }
          else if (((*(char *)(lVar7 + -0x5a6601071b4f6180) == '\x15') &&
                   (lVar9 = FUN_18043b320(*(undefined4 *)*puVar6), lVar9 != 0)) &&
                  ((*(char *)(lVar9 + 0x137) != '\0' &&
                   ((*(uint *)(lVar7 + -0x5a6601071b4f6182) & 0x40000000) == 0))))
          goto LAB_1804434e2;
          lVar7 = *(longlong *)(lVar18 + 0x10);
          local_res8 = puVar6;
          if ((~(byte)(*(uint *)(lVar7 + -0x5a6601071b4f6182) >> 4) & 1) == 0) {
            if ((*(byte *)(lVar7 + -0x5a6601071b4f6182) & 0x10) != 0) {
              if ((*(int *)(lVar18 + 0x1c) == 0x7f804674) ||
                 ((*(byte *)(lVar7 + -0x5a6601071b4f6182) & 0x40) != 0)) {
                if (((*(byte *)(lVar7 + -0x5a6601071b4f6182) & 0x10) != 0) &&
                   ((*(int *)(lVar18 + 0x1c) == 0x7f804674 &&
                    ((*(byte *)(lVar7 + -0x5a6601071b4f6182) & 0x40) == 0)))) {
                  if ((&local_res8 < ppuStack_100) && (local_108 <= &local_res8)) {
                    lVar7 = (longlong)&local_res8 - (longlong)local_108;
                    if (ppuStack_100 == local_f8) {
                      FUN_180450cc0(&local_108,1);
                    }
                    if (ppuStack_100 != (undefined8 **)0x0) {
                      *ppuStack_100 = local_108[lVar7 >> 3];
                    }
                  }
                  else {
                    if (ppuStack_100 == local_f8) {
                      FUN_180450cc0(&local_108,1);
                    }
                    if (ppuStack_100 != (undefined8 **)0x0) {
                      *ppuStack_100 = puVar6;
                    }
                  }
                  ppuStack_100 = ppuStack_100 + 1;
                }
              }
              else if ((&local_res8 < ppuStack_130) && (local_138 <= &local_res8)) {
                lVar7 = (longlong)&local_res8 - (longlong)local_138;
                if ((ppuStack_130 == local_128) &&
                   ((longlong)local_128 - (longlong)ppuStack_130 >> 3 == 0)) {
                  lVar18 = (longlong)ppuStack_130 - (longlong)local_138 >> 3;
                  if (lVar18 == 0x1fffffffffffffff) {
                    /* WARNING: Subroutine does not return */
                    FUN_1804fe5b8("vector<T> too long");
                  }
                  puVar6 = (undefined8 *)(lVar18 + 1);
                  uVar16 = (longlong)local_128 - (longlong)local_138 >> 3;
                  puVar11 = puVar13;
                  if (uVar16 <= 0x1fffffffffffffff - (uVar16 >> 1)) {
                    puVar11 = (undefined8 *)((uVar16 >> 1) + uVar16);
                  }
                  if (puVar6 <= puVar11) {
                    puVar6 = puVar11;
                  }
                  FUN_1804109f0(&local_138,puVar6);
                }
                if (ppuStack_130 != (undefined8 **)0x0) {
                  *ppuStack_130 = local_138[lVar7 >> 3];
                }
                ppuStack_130 = ppuStack_130 + 1;
              }
              else {
                if ((ppuStack_130 == local_128) &&
                   ((longlong)local_128 - (longlong)ppuStack_130 >> 3 == 0)) {
                  lVar7 = (longlong)ppuStack_130 - (longlong)local_138 >> 3;
                  if (lVar7 == 0x1fffffffffffffff) {
                    /* WARNING: Subroutine does not return */
                    FUN_1804fe5b8("vector<T> too long");
                  }
                  puVar11 = (undefined8 *)(lVar7 + 1);
                  uVar16 = (longlong)local_128 - (longlong)local_138 >> 3;
                  puVar12 = puVar13;
                  if (uVar16 <= 0x1fffffffffffffff - (uVar16 >> 1)) {
                    puVar12 = (undefined8 *)((uVar16 >> 1) + uVar16);
                  }
                  if (puVar11 <= puVar12) {
                    puVar11 = puVar12;
                  }
                  FUN_1804109f0(&local_138,puVar11);
                }
                if (ppuStack_130 != (undefined8 **)0x0) {
                  *ppuStack_130 = puVar6;
                }
                ppuStack_130 = ppuStack_130 + 1;
              }
            }
          }
          else if ((&local_res8 < ppuStack_118) && (local_120 <= &local_res8)) {
            lVar7 = (longlong)&local_res8 - (longlong)local_120;
            if ((ppuStack_118 == local_110) &&
               ((longlong)local_110 - (longlong)ppuStack_118 >> 3 == 0)) {
              lVar18 = (longlong)ppuStack_118 - (longlong)local_120 >> 3;
              if (lVar18 == 0x1fffffffffffffff) {
                    /* WARNING: Subroutine does not return */
                FUN_1804fe5b8("vector<T> too long");
              }
              puVar6 = (undefined8 *)(lVar18 + 1);
              uVar16 = (longlong)local_110 - (longlong)local_120 >> 3;
              puVar11 = puVar13;
              if (uVar16 <= 0x1fffffffffffffff - (uVar16 >> 1)) {
                puVar11 = (undefined8 *)((uVar16 >> 1) + uVar16);
              }
              if (puVar6 <= puVar11) {
                puVar6 = puVar11;
              }
              FUN_1804109f0(&local_120,puVar6);
            }
            if (ppuStack_118 != (undefined8 **)0x0) {
              *ppuStack_118 = local_120[lVar7 >> 3];
            }
            ppuStack_118 = ppuStack_118 + 1;
          }
          else {
            if ((ppuStack_118 == local_110) &&
               ((longlong)local_110 - (longlong)ppuStack_118 >> 3 == 0)) {
              lVar7 = (longlong)ppuStack_118 - (longlong)local_120 >> 3;
              if (lVar7 == 0x1fffffffffffffff) {
                    /* WARNING: Subroutine does not return */
                FUN_1804fe5b8("vector<T> too long");
              }
              puVar11 = (undefined8 *)(lVar7 + 1);
              uVar16 = (longlong)local_110 - (longlong)local_120 >> 3;
              puVar12 = puVar13;
              if (uVar16 <= 0x1fffffffffffffff - (uVar16 >> 1)) {
                puVar12 = (undefined8 *)((uVar16 >> 1) + uVar16);
              }
              if (puVar11 <= puVar12) {
                puVar11 = puVar12;
              }
              FUN_1804109f0(&local_120,puVar11);
            }
            if (ppuStack_118 != (undefined8 **)0x0) {
              *ppuStack_118 = puVar6;
            }
            ppuStack_118 = ppuStack_118 + 1;
          }
          uVar19 = uVar19 + 1;
        } while (uVar19 < *(ushort *)(param_1 + 0x12a));
      }
      local_d0[0] = 0;
      local_d0[1] = 0;
      local_d0[2] = 0;
      local_60[0] = 0;
      local_60[1] = 0;
      local_60[2] = 0;
      local_90[0] = 0;
      local_90[1] = 0;
      local_90[2] = 0;
      FUN_1804ecfb0(uVar5,uVar17,*(undefined1 *)(param_1 + 0x133),*(undefined1 *)(param_1 + 0x130),
                    &local_120,local_d0);
      *(undefined1 *)(param_1 + 0x135) = local_a7;
      uVar16 = local_d0[3];
      if ((*(char *)(param_1 + 0x142) != '\0') &&
         ((ulonglong)((longlong)ppuStack_118 - (longlong)local_120) < 8)) {
        uVar16 = 0x11;
        *(undefined4 *)(param_1 + 0x11c) = 0x11;
      }
      if (*(undefined4 **)(param_1 + 0xc0) != (undefined4 *)0x0) {
        lVar7 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
        uVar2 = *(uint *)(lVar7 + 0x114);
        if ((uVar2 != 0) && (uVar16 < uVar2)) {
          uVar16 = (ulonglong)uVar2;
        }
        *(int *)(param_1 + 0x114) = (int)uVar16;
      }
      *(undefined1 *)(param_1 + 0x138) = 1;
      FUN_1804ecfb0(0,0,1,0,&local_138,local_60);
      FUN_1804ecfb0(0,0,1,0,&local_108,local_90);
      *(undefined1 *)(param_1 + 0x133) = local_a8;
      *(undefined4 *)(param_1 + 0x11c) = local_b0;
      if (*(longlong *)(param_1 + 0xc0) != 0) {
        *(int *)(param_1 + 0x114) = (int)uVar16;
        if (((*(byte *)(param_1 + 0x10c) & 0x10) == 0) &&
           (puVar6 = puVar13, uVar19 = uVar14, *(short *)(param_1 + 0x12a) != 0)) {
          do {
            lVar7 = (ulonglong)uVar19 * 0x20 + *(longlong *)(param_1 + 0x10);
            if ((*(byte *)(*(longlong *)(lVar7 + 0x10) + -0x5a6601071b4f6182) & 0x10) == 0) {
              *(int *)(lVar7 + 0x1c) = *(int *)((longlong)puVar6 + local_d0[0]) + 0x7f804675;
              puVar6 = puVar6 + 1;
            }
            uVar19 = uVar19 + 1;
          } while (uVar19 < *(ushort *)(param_1 + 0x12a));
        }
        *(undefined4 *)(param_1 + 0x110) = local_48;
        if (((*(byte *)(param_1 + 0x10c) & 0x10) == 0) &&
           (puVar6 = puVar13, uVar19 = uVar14, *(short *)(param_1 + 0x12a) != 0)) {
          do {
            lVar7 = (ulonglong)uVar19 * 0x20 + *(longlong *)(param_1 + 0x10);
            if (((*(byte *)(*(longlong *)(lVar7 + 0x10) + -0x5a6601071b4f6182) & 0x10) != 0) &&
               ((*(int *)(lVar7 + 0x1c) != 0x7f804674 &&
                ((*(byte *)(*(longlong *)(lVar7 + 0x10) + -0x5a6601071b4f6182) & 0x40) == 0)))) {
              *(int *)(lVar7 + 0x1c) = *(int *)((longlong)puVar6 + local_60[0]) + 0x7f804675;
              puVar6 = puVar6 + 1;
            }
            uVar19 = uVar19 + 1;
          } while (uVar19 < *(ushort *)(param_1 + 0x12a));
        }
        *(undefined4 *)(param_1 + 0x104) = local_78;
        if (((*(byte *)(param_1 + 0x10c) & 0x10) == 0) && (*(short *)(param_1 + 0x12a) != 0)) {
          do {
            lVar7 = (ulonglong)uVar14 * 0x20 + *(longlong *)(param_1 + 0x10);
            if (((*(byte *)(*(longlong *)(lVar7 + 0x10) + -0x5a6601071b4f6182) & 0x10) != 0) &&
               ((*(int *)(lVar7 + 0x1c) == 0x7f804674 &&
                ((*(byte *)(*(longlong *)(lVar7 + 0x10) + -0x5a6601071b4f6182) & 0x40) == 0)))) {
              *(undefined4 *)(lVar7 + 0x1c) = 0x7f804674;
              local_98 = *(undefined4 *)((longlong)puVar13 + local_90[0]);
              local_a0 = lVar7;
              FUN_180421430(&DAT_1899db520,&local_f0,&local_a0,&local_a0);
              puVar13 = puVar13 + 1;
            }
            uVar14 = uVar14 + 1;
          } while (uVar14 < *(ushort *)(param_1 + 0x12a));
        }
      }
      if (local_90[0] != 0) {
        FUN_180452930(local_90,local_90[0],local_90[2] - local_90[0] >> 3);
        local_90[0] = 0;
        local_90[1] = 0;
        local_90[2] = 0;
      }
      if (local_60[0] != 0) {
        FUN_180452930(local_60,local_60[0],local_60[2] - local_60[0] >> 3);
        local_60[0] = 0;
        local_60[1] = 0;
        local_60[2] = 0;
      }
      if (local_d0[0] != 0) {
        FUN_180452930(local_d0,local_d0[0],local_d0[2] - local_d0[0] >> 3);
        local_d0[0] = 0;
        local_d0[1] = 0;
        local_d0[2] = 0;
      }
      if (local_108 != (undefined8 **)0x0) {
        FUN_180452930(&local_108,local_108,(longlong)local_f8 - (longlong)local_108 >> 3);
        local_108 = (undefined8 **)0x0;
        ppuStack_100 = (undefined8 **)0x0;
        local_f8 = (undefined8 **)0x0;
      }
      if (local_138 != (undefined8 **)0x0) {
        FUN_180452930(&local_138,local_138,(longlong)local_128 - (longlong)local_138 >> 3);
        local_138 = (undefined8 **)0x0;
        ppuStack_130 = (undefined8 **)0x0;
        local_128 = (undefined8 **)0x0;
      }
      if (local_120 != (undefined8 **)0x0) {
        FUN_180452930(&local_120,local_120,(longlong)local_110 - (longlong)local_120 >> 3);
      }
    }
    if (*(int *)(param_1 + 0x110) != 0) {
      uVar8 = thunk_FUN_1804df2c0(*(int *)(param_1 + 0x110),0);
      *(undefined8 *)(param_1 + 0x28) = uVar8;
      DAT_1899db850 = DAT_1899db850 + 1;
      if ((DAT_1899db858 & 0x7fffffffffffffff) < DAT_1899db850) {
        lVar7 = DAT_1899db858 * 2;
        if (lVar7 == 0) {
          lVar7 = 1;
        }
        FUN_1804536f0(&DAT_1899db848,lVar7);
      }
      *(longlong *)(DAT_1899db848 + -8 + DAT_1899db850 * 8) = param_1;
    }
    if (*(int *)(param_1 + 0x104) != 0) {
      uVar5 = FUN_18042bf60();
      *(undefined4 *)(param_1 + 0x118) = uVar5;
    }
  }
  return;
}



