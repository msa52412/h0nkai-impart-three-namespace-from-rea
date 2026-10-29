// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x180448970 ================= */
/* name   = FUN_180448970 */
/* entry  = 180448970 */
/* body   = 86 bytes */
/* sig    = undefined FUN_180448970() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_180448970(void)

{
  code *pcVar1;
  undefined8 uVar2;
  undefined8 auStackX_8 [4];
  
  uVar2 = FUN_18042d650(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a1f38);
  uVar2 = FUN_1804457f0(uVar2);
  FUN_180446020(uVar2,0);
  FUN_180447cf0(uVar2,0);
  auStackX_8[0] = uVar2;
  FUN_1804ff8e0(auStackX_8,&UNK_188d08588);
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



/* ================= 0x180448320 ================= */
/* name   = FUN_180448320 */
/* entry  = 180448320 */
/* body   = 37 bytes */
/* sig    = undefined FUN_180448320() */


void FUN_180448320(undefined8 param_1)

{
  code *pcVar1;
  undefined8 auStackX_8 [4];
  
  FUN_180447cf0();
  auStackX_8[0] = param_1;
  FUN_1804ff8e0(auStackX_8,&UNK_188d08588);
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



/* ================= 0x180448910 ================= */
/* name   = FUN_180448910 */
/* entry  = 180448910 */
/* body   = 89 bytes */
/* sig    = undefined FUN_180448910() */


void FUN_180448910(longlong *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined8 *puVar1;
  undefined1 auStack_30 [48];
  
  if (param_1[1] == 0) {
    if (*param_1 != 0) {
      puVar1 = (undefined8 *)FUN_1804354b0(auStack_30,param_1,param_3,param_4,0xfffffffffffffffe);
      if (0xf < (ulonglong)puVar1[3]) {
        puVar1 = (undefined8 *)*puVar1;
      }
      FUN_1804488a0(puVar1);
    }
    puVar1 = (undefined8 *)FUN_180438ec0();
    if (0xf < (ulonglong)puVar1[3]) {
      puVar1 = (undefined8 *)*puVar1;
    }
    FUN_1804488a0(puVar1);
  }
  return;
}



/* ================= 0x180449980 ================= */
/* name   = FUN_180449980 */
/* entry  = 180449980 */
/* body   = 728 bytes */
/* sig    = undefined FUN_180449980() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_180449980(ulonglong *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  short *psVar1;
  code *pcVar2;
  char cVar3;
  longlong lVar4;
  undefined8 *puVar5;
  longlong lVar6;
  undefined8 uVar7;
  ulonglong uVar8;
  longlong lStackX_8;
  ulonglong uStack_58;
  ulonglong uStack_50;
  longlong lStack_48;
  undefined8 uStack_40;
  ulonglong auStack_38 [3];
  ulonglong uStack_20;
  
  lVar4 = FUN_1803f2e20(param_1,param_1 + 2,param_3,param_4,0xfffffffffffffffe);
  if (lVar4 == 0) {
    puVar5 = (undefined8 *)FUN_180445710(auStack_38,*param_1);
    if (0xf < (ulonglong)puVar5[3]) {
      puVar5 = (undefined8 *)*puVar5;
    }
    cVar3 = func_0x0001804fd340(puVar5,&UNK_1881a2518);
    if (0xf < uStack_20) {
      uVar8 = auStack_38[0];
      if (0xfff < uStack_20 + 1) {
        if ((auStack_38[0] & 0x1f) != 0) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
        uVar8 = *(ulonglong *)(auStack_38[0] - 8);
        if (auStack_38[0] <= uVar8) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
        if (auStack_38[0] - uVar8 < 8) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
        if (0x27 < auStack_38[0] - uVar8) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
      }
      thunk_FUN_18050a3b8(uVar8);
    }
    lVar4 = 0;
    if (cVar3 == '\0') {
      uStack_58 = *param_1;
      uStack_50 = param_1[1];
    }
    else {
      uStack_58 = 0;
      uStack_50 = 0;
    }
    lVar6 = FUN_180443ee0(&uStack_58);
    if (lVar6 == 0) {
      uStack_40 = 7;
      lStack_48 = 0;
      uStack_58 = uStack_58 & 0xffffffffffff0000;
      FUN_180451640(&uStack_58,&UNK_1881a2530,0x14);
      psVar1 = (short *)*param_1;
      if (*psVar1 != 0) {
        lVar4 = -1;
        do {
          lVar4 = lVar4 + 1;
        } while (psVar1[lVar4] != 0);
      }
      FUN_180451640(&uStack_58,psVar1,lVar4);
      FUN_180451640(&uStack_58,&UNK_1881a2560,0x2b);
      puVar5 = (undefined8 *)FUN_1804f32f0(auStack_38,&uStack_58);
      if (0xf < (ulonglong)puVar5[3]) {
        puVar5 = (undefined8 *)*puVar5;
      }
      lVar4 = FUN_1804303f0(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a20c0,puVar5);
      FUN_180447cf0(lVar4,0);
      lStackX_8 = lVar4;
      lVar6 = FUN_1804ff8e0(&lStackX_8,&UNK_188d08588);
    }
    lVar6 = FUN_1803f2bf0(lVar6,param_1);
    if (lVar6 == 0) {
      uStack_40 = 7;
      uStack_58 = CONCAT62(uStack_58._2_6_,(short)lVar4);
      lStack_48 = lVar4;
      FUN_180451640(&uStack_58,&UNK_1881a25c0,0x25);
      uVar7 = FUN_1803f73c0(auStack_38,param_1[2]);
      FUN_180451510(&uStack_58,uVar7,0,0xffffffffffffffff);
      if (7 < uStack_20) {
        FUN_1803f9830(auStack_38,auStack_38[0],uStack_20 + 1);
      }
      FUN_180451640(&uStack_58,&UNK_1881a2610,6);
      psVar1 = (short *)*param_1;
      if (*psVar1 != 0) {
        lVar4 = -1;
        do {
          lVar4 = lVar4 + 1;
        } while (psVar1[lVar4] != 0);
      }
      FUN_180451640(&uStack_58,psVar1,lVar4);
      FUN_180451640(&uStack_58,&UNK_1881a2620,2);
      puVar5 = (undefined8 *)FUN_1804f32f0(auStack_38,&uStack_58);
      if (0xf < (ulonglong)puVar5[3]) {
        puVar5 = (undefined8 *)*puVar5;
      }
      lVar4 = FUN_1804303f0(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a20a0,puVar5);
      FUN_180447cf0(lVar4,0);
      lStackX_8 = lVar4;
      FUN_1804ff8e0(&lStackX_8,&UNK_188d08588);
    }
  }
  return;
}



/* ================= 0x180442320 ================= */
/* name   = FUN_180442320 */
/* entry  = 180442320 */
/* body   = 183 bytes */
/* sig    = undefined FUN_180442320() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong * FUN_180442320(longlong *param_1,longlong param_2)

{
  char cVar1;
  longlong lVar2;
  longlong *plVar3;
  
  if (param_1 == (longlong *)0x0) {
    return (longlong *)0x0;
  }
  lVar2 = *param_1;
  cVar1 = FUN_180441540(param_2,lVar2);
  if (cVar1 != '\0') {
    return param_1;
  }
  if (*(char *)(lVar2 + 0x141) == '\0') {
    return (longlong *)0x0;
  }
  if (((((*(byte *)(param_2 + 0x10c) & 0x20) != 0) || (*(char *)(param_2 + 0x6a) == '\x13')) ||
      (*(char *)(param_2 + 0x6a) == '\x1e')) &&
     (((*(longlong *)(param_2 + 0x48) != 0 &&
       (*(longlong *)(*(longlong *)(param_2 + 0x48) + 0x28) != 0)) &&
      (lVar2 = FUN_180417700(param_1), lVar2 != 0)))) {
    return param_1;
  }
  plVar3 = (longlong *)0x0;
  if (param_2 == _DAT_1899db1c8) {
    plVar3 = param_1;
  }
  return plVar3;
}



/* ================= 0x180441540 ================= */
/* name   = FUN_180441540 */
/* entry  = 180441540 */
/* body   = 2647 bytes */
/* sig    = undefined FUN_180441540() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

bool FUN_180441540(longlong param_1,longlong param_2)

{
  short sVar1;
  int *piVar2;
  char cVar3;
  ushort uVar4;
  longlong lVar5;
  longlong lVar6;
  longlong lVar7;
  longlong lVar8;
  uint uVar10;
  ulonglong uVar11;
  ulonglong uVar12;
  int iVar13;
  ulonglong uVar14;
  longlong lStackX_8;
  ulonglong uStackX_10;
  ulonglong uStackX_18;
  longlong lStackX_20;
  uint *puStack_68;
  longlong lStack_60;
  longlong lStack_48;
  uint *puStack_40;
  undefined8 uStack_38;
  ulonglong uVar9;
  
  uStack_38 = 0xfffffffffffffffe;
  lStackX_8 = param_1;
  lStackX_20 = param_2;
  if (param_1 == param_2) {
    return true;
  }
  do {
    if (*(char *)(lStackX_8 + 0x13f) == '\0') {
      uStackX_10 = 0x1899db6b0;
      func_0x0001803f4990(0x1899db6b0);
      FUN_18043e550(lStackX_8,&uStackX_10);
      func_0x0001803f72c0(uStackX_10);
    }
    if (*(char *)(param_2 + 0x13f) == '\0') {
      uStackX_10 = 0x1899db6b0;
      func_0x0001803f4990(0x1899db6b0);
      FUN_18043e550(param_2,&uStackX_10);
      func_0x0001803f72c0(uStackX_10);
    }
    if ((((*(byte *)(lStackX_8 + 0x10c) & 0x20) != 0) || (*(char *)(lStackX_8 + 0x6a) == '\x13')) ||
       (*(char *)(lStackX_8 + 0x6a) == '\x1e')) {
      uVar11 = 0;
      if (*(uint **)(lStackX_8 + 0xc0) == (uint *)0x0) {
        do {
          uVar11 = 0;
          if (*(ushort *)(param_2 + 300) != 0) {
            do {
              if (*(longlong *)(*(longlong *)(param_2 + 0x38) + uVar11 * 8) == lStackX_8) {
                return true;
              }
              uVar4 = (short)uVar11 + 1;
              uVar11 = (ulonglong)uVar4;
            } while (uVar4 < *(ushort *)(param_2 + 300));
          }
          uVar11 = 0;
          if (*(ushort *)(param_2 + 0x12e) != 0) {
            do {
              if (*(longlong *)(uVar11 * 0x10 + *(longlong *)(param_2 + 0x70)) == lStackX_8) {
                return true;
              }
              uVar4 = (short)uVar11 + 1;
              uVar11 = (ulonglong)uVar4;
            } while (uVar4 < *(ushort *)(param_2 + 0x12e));
          }
          param_2 = *(longlong *)(param_2 + 0x80);
        } while (param_2 != 0);
        return false;
      }
      uVar10 = **(uint **)(lStackX_8 + 0xc0);
      iVar13 = 0;
      uVar9 = uVar11;
      if (uVar10 != 0xffffffff) {
        iVar13 = ((int)((ulonglong)uVar10 * 0x1f17946ef935 + 0xafd81baecafdac6 >> 0x15) + 0x54760499
                 ) * 0x1125f1b6;
        uVar9 = (ulonglong)uVar10 * 0x5c + ((longlong)_DAT_188198e08 ^ 0x2b849db3U) + _DAT_1899dbaf8
        ;
      }
      uVar10 = (*(int *)(uVar9 + 0x3c) - iVar13) + 0xdcfc519d;
      if (uVar10 == 0xffffffff) {
        lStack_60 = 0;
        puStack_68 = (uint *)0x0;
      }
      else {
        lStack_60 = (((((ulonglong)uVar10 * 0x6ae9 ^ 0x2e6f3e3d) * 0x2ad3dd28 >> 0x16) * 0x4c39b37d
                     ^ 0x137ea9ac000) >> 10) * 0x22449c6e;
        puStack_68 = (uint *)((ulonglong)uVar10 * 0x10 +
                             ((longlong)_DAT_188198e00 ^ 0x7497c9eeU) + _DAT_1899dbaf8);
      }
      while( true ) {
        piVar2 = *(int **)(param_2 + 0xc0);
        iVar13 = (int)lStack_60;
        if ((piVar2 != (int *)0x0) && (*piVar2 == **(int **)(lStackX_8 + 0xc0))) break;
LAB_180441b61:
        uVar9 = 0;
        uStackX_10 = uStackX_10 & 0xffffffffffff0000;
        if (*(short *)(lStackX_20 + 300) != 0) {
          do {
            piVar2 = *(int **)(*(longlong *)(*(longlong *)(lStackX_20 + 0x38) + uVar9 * 8) + 0xc0);
            if ((piVar2 != (int *)0x0) && (*piVar2 == **(int **)(lStackX_8 + 0xc0))) {
              lStack_48 = *(longlong *)(*(int **)(lStackX_8 + 0xc0) + 2);
              lVar5 = *(longlong *)(piVar2 + 2);
              uStackX_18 = uStackX_18 & 0xffffffff00000000;
              lVar6 = (longlong)(int)((*puStack_68 ^ 0x13c7ef8b) - iVar13);
              uVar9 = uVar11;
              uVar12 = uVar11;
              if (lVar6 < 1) {
                return true;
              }
              do {
                uVar10 = (int)uVar9 + -0x4206a291 + (puStack_68[2] - iVar13);
                uVar9 = uVar11;
                uVar14 = uVar11;
                if (uVar10 != 0xffffffff) {
                  uVar9 = ((ulonglong)uVar10 * 0x34d04ba0e4db + 0xa13ee8c44cc682a ^ 0x43427e7d) +
                          0x10776301;
                  uVar14 = (ulonglong)uVar10 * 0x10 +
                           (_DAT_188198e40 + -0x77870e75) + _DAT_1899dbaf8;
                }
                sVar1 = *(short *)(uVar14 + 10);
                lVar7 = FUN_180430150(*(undefined8 *)(*(longlong *)(lStack_48 + 8) + uVar12 * 8),
                                      CONCAT71((int7)(uVar9 >> 8),1));
                lVar8 = FUN_180430150(*(undefined8 *)(*(longlong *)(lVar5 + 8) + uVar12 * 8),1);
                uVar10 = ((uint)(ushort)(sVar1 - 2) ^ (uint)uVar9) & 3;
                if (((uVar10 == 0) || (*(char *)(lVar7 + 0x142) != '\0')) ||
                   (*(char *)(lVar8 + 0x142) != '\0')) {
                  if (lVar7 != lVar8) break;
                }
                else {
                  if (uVar10 == 1) {
                    cVar3 = FUN_180441540(lVar7,lVar8);
                  }
                  else {
                    cVar3 = FUN_180441540(lVar8,lVar7);
                  }
                  if (cVar3 == '\0') break;
                }
                uVar9 = (ulonglong)((int)uStackX_18 + 1U);
                uStackX_18 = CONCAT44(uStackX_18._4_4_,(int)uStackX_18 + 1U);
                uVar12 = uVar12 + 1;
                if (lVar6 <= (longlong)uVar12) {
                  return true;
                }
              } while( true );
            }
            uVar4 = (short)uStackX_10 + 1;
            uVar9 = (ulonglong)uVar4;
            uStackX_10 = CONCAT62(uStackX_10._2_6_,uVar4);
          } while (uVar4 < *(ushort *)(lStackX_20 + 300));
        }
        uVar9 = 0;
        uStackX_10 = uStackX_10 & 0xffffffffffff0000;
        if (*(short *)(lStackX_20 + 0x12e) != 0) {
          do {
            piVar2 = *(int **)(*(longlong *)(*(longlong *)(lStackX_20 + 0x70) + uVar9 * 0x10) + 0xc0
                              );
            if ((piVar2 != (int *)0x0) && (*piVar2 == **(int **)(lStackX_8 + 0xc0))) {
              lVar5 = *(longlong *)(*(int **)(lStackX_8 + 0xc0) + 2);
              lStack_48 = *(longlong *)(piVar2 + 2);
              uStackX_18 = uStackX_18 & 0xffffffff00000000;
              lVar6 = (longlong)(int)((*puStack_68 ^ 0x13c7ef8b) - iVar13);
              uVar9 = uVar11;
              uVar12 = uVar11;
              if (lVar6 < 1) {
                return true;
              }
              do {
                uVar10 = puStack_68[2] + 0xbdf95d6f + ((int)uVar9 - iVar13);
                uVar9 = uVar11;
                uVar14 = uVar11;
                if (uVar10 != 0xffffffff) {
                  uVar9 = ((ulonglong)uVar10 * 0x34d04ba0e4db + 0xa13ee8c44cc682a ^ 0x43427e7d) +
                          0x10776301;
                  uVar14 = (ulonglong)uVar10 * 0x10 +
                           (_DAT_188198e40 + -0x77870e75) + _DAT_1899dbaf8;
                }
                sVar1 = *(short *)(uVar14 + 10);
                lVar7 = FUN_180430150(*(undefined8 *)(*(longlong *)(lVar5 + 8) + uVar12 * 8),
                                      CONCAT71((int7)(uVar9 >> 8),1));
                lVar8 = FUN_180430150(*(undefined8 *)(*(longlong *)(lStack_48 + 8) + uVar12 * 8),1);
                uVar10 = ((uint)(ushort)(sVar1 - 2) ^ (uint)uVar9) & 3;
                if (((uVar10 == 0) || (*(char *)(lVar7 + 0x142) != '\0')) ||
                   (*(char *)(lVar8 + 0x142) != '\0')) {
                  if (lVar7 != lVar8) break;
                }
                else {
                  if (uVar10 == 1) {
                    cVar3 = FUN_180441540(lVar7,lVar8);
                  }
                  else {
                    cVar3 = FUN_180441540(lVar8,lVar7);
                  }
                  if (cVar3 == '\0') break;
                }
                uVar9 = (ulonglong)((int)uStackX_18 + 1U);
                uStackX_18 = CONCAT44(uStackX_18._4_4_,(int)uStackX_18 + 1U);
                uVar12 = uVar12 + 1;
                if (lVar6 <= (longlong)uVar12) {
                  return true;
                }
              } while( true );
            }
            uVar4 = (short)uStackX_10 + 1;
            uVar9 = (ulonglong)uVar4;
            uStackX_10 = CONCAT62(uStackX_10._2_6_,uVar4);
          } while (uVar4 < *(ushort *)(lStackX_20 + 0x12e));
        }
        param_2 = *(longlong *)(lStackX_20 + 0x80);
        lStackX_20 = param_2;
        if (param_2 == 0) {
          return false;
        }
      }
      lVar5 = *(longlong *)(*(int **)(lStackX_8 + 0xc0) + 2);
      uStackX_18 = *(ulonglong *)(piVar2 + 2);
      uStackX_10 = uStackX_10 & 0xffffffff00000000;
      lVar6 = (longlong)(int)((*puStack_68 ^ 0x13c7ef8b) - iVar13);
      uVar9 = uVar11;
      uVar12 = uVar11;
      if (lVar6 < 1) {
        return true;
      }
      do {
        uVar10 = (int)uVar9 + -0x4206a291 + (puStack_68[2] - iVar13);
        uVar9 = uVar11;
        uVar14 = uVar11;
        if (uVar10 != 0xffffffff) {
          uVar9 = ((ulonglong)uVar10 * 0x34d04ba0e4db + 0xa13ee8c44cc682a ^ 0x43427e7d) + 0x10776301
          ;
          uVar14 = (ulonglong)uVar10 * 0x10 + (_DAT_188198e40 + -0x77870e75) + _DAT_1899dbaf8;
        }
        sVar1 = *(short *)(uVar14 + 10);
        lVar7 = FUN_180430150(*(undefined8 *)(*(longlong *)(lVar5 + 8) + uVar12 * 8),
                              CONCAT71((int7)(uVar9 >> 8),1));
        lVar8 = FUN_180430150(*(undefined8 *)(*(longlong *)(uStackX_18 + 8) + uVar12 * 8),1);
        uVar10 = ((uint)(ushort)(sVar1 - 2) ^ (uint)uVar9) & 3;
        if (((uVar10 == 0) || (*(char *)(lVar7 + 0x142) != '\0')) ||
           (*(char *)(lVar8 + 0x142) != '\0')) {
          if (lVar7 != lVar8) goto LAB_180441b61;
        }
        else {
          if (uVar10 == 1) {
            cVar3 = FUN_180441540(lVar7,lVar8);
          }
          else {
            cVar3 = FUN_180441540(lVar8,lVar7);
          }
          if (cVar3 == '\0') goto LAB_180441b61;
        }
        uVar9 = (ulonglong)((int)uStackX_10 + 1U);
        uStackX_10 = CONCAT44(uStackX_10._4_4_,(int)uStackX_10 + 1U);
        uVar12 = uVar12 + 1;
        if (lVar6 <= (longlong)uVar12) {
          return true;
        }
      } while( true );
    }
    if (*(char *)(lStackX_8 + 0x131) == '\0') {
      if (lStackX_8 == _DAT_1899db1c8) {
        return true;
      }
      cVar3 = FUN_180442470(lStackX_8);
      if (cVar3 == '\0') {
        uVar11 = 0;
        if ((*(longlong *)(lStackX_8 + 0x80) != _DAT_1899db268) ||
           (*(undefined4 **)(lStackX_8 + 0xc0) == (undefined4 *)0x0)) goto LAB_1804418af;
        func_0x00018043b290(&lStack_48,**(undefined4 **)(lStackX_8 + 0xc0));
        func_0x0001804358c0(&lStack_48,(puStack_40[0xf] - (int)lStack_48) + -0x2303ae63);
        piVar2 = *(int **)(param_2 + 0xc0);
        if ((piVar2 == (int *)0x0) || (*piVar2 != **(int **)(lStackX_8 + 0xc0))) goto LAB_1804418af;
        lVar5 = *(longlong *)(*(int **)(lStackX_8 + 0xc0) + 2);
        uStackX_18 = *(ulonglong *)(piVar2 + 2);
        uStackX_10 = uStackX_10 & 0xffffffff00000000;
        lVar6 = (longlong)(int)((*puStack_40 ^ 0x13c7ef8b) - (int)lStack_48);
        uVar9 = uVar11;
        uVar12 = uVar11;
        if (lVar6 < 1) {
          return true;
        }
        break;
      }
      FUN_180442470(param_2);
      lStackX_8 = FUN_180430150(**(undefined8 **)
                                  (*(longlong *)(*(longlong *)(lStackX_8 + 0xc0) + 8) + 8),1);
    }
    else {
      if (*(char *)(param_2 + 0x131) != *(char *)(lStackX_8 + 0x131)) {
        return false;
      }
      lVar5 = *(longlong *)(param_2 + 0x98);
      if (*(char *)(lVar5 + 0x142) != '\0') {
        lVar5 = func_0x00018043a270(*(undefined8 *)(lStackX_8 + 0x98));
        lVar6 = func_0x00018043a270(*(undefined8 *)(param_2 + 0x98));
        return lVar5 == lVar6;
      }
      lStackX_8 = *(longlong *)(lStackX_8 + 0x98);
      param_2 = lVar5;
      lStackX_20 = lVar5;
    }
    if (lStackX_8 == param_2) {
      return true;
    }
  } while( true );
LAB_180441791:
  uVar10 = (int)uVar9 + -0x4206a291 + (puStack_40[2] - (int)lStack_48);
  uVar9 = uVar11;
  uVar14 = uVar11;
  if (uVar10 != 0xffffffff) {
    uVar9 = ((ulonglong)uVar10 * 0x34d04ba0e4db + 0xa13ee8c44cc682a ^ 0x43427e7d) + 0x10776301;
    uVar14 = (ulonglong)uVar10 * 0x10 + (_DAT_188198e40 + -0x77870e75) + _DAT_1899dbaf8;
  }
  sVar1 = *(short *)(uVar14 + 10);
  lVar7 = FUN_180430150(*(undefined8 *)(*(longlong *)(lVar5 + 8) + uVar12 * 8),
                        CONCAT71((int7)(uVar9 >> 8),1));
  lVar8 = FUN_180430150(*(undefined8 *)(*(longlong *)(uStackX_18 + 8) + uVar12 * 8),1);
  uVar10 = ((uint)(ushort)(sVar1 - 2) ^ (uint)uVar9) & 3;
  if (((uVar10 == 0) || (*(char *)(lVar7 + 0x142) != '\0')) || (*(char *)(lVar8 + 0x142) != '\0')) {
    param_2 = lStackX_20;
    if (lVar7 != lVar8) goto LAB_1804418af;
  }
  else {
    if (uVar10 == 1) {
      cVar3 = FUN_180441540(lVar7,lVar8);
    }
    else {
      cVar3 = FUN_180441540(lVar8,lVar7);
    }
    param_2 = lStackX_20;
    if (cVar3 == '\0') {
LAB_1804418af:
      if (*(byte *)(param_2 + 0x132) < *(byte *)(lStackX_8 + 0x132)) {
        return false;
      }
      if (*(longlong *)
           (*(longlong *)(param_2 + 0x50) + (longlong)(int)(*(byte *)(lStackX_8 + 0x132) - 1) * 8)
          == lStackX_8) {
        return true;
      }
      return false;
    }
  }
  uVar10 = (int)uStackX_10 + 1;
  uStackX_10 = CONCAT44(uStackX_10._4_4_,uVar10);
  uVar12 = uVar12 + 1;
  uVar9 = (ulonglong)uVar10;
  if (lVar6 <= (longlong)uVar12) {
    return true;
  }
  goto LAB_180441791;
}



/* ================= 0x180431fb0 ================= */
/* name   = FUN_180431fb0 */
/* entry  = 180431fb0 */
/* body   = 93 bytes */
/* sig    = undefined FUN_180431fb0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_180431fb0(void)

{
  undefined8 uVar1;
  undefined8 in_R9;
  
  uVar1 = FUN_18042d650(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a2080,in_R9,0xfffffffffffffffe,0);
  uVar1 = FUN_1804457f0(uVar1);
  FUN_180446020(uVar1,0);
  return uVar1;
}



/* ================= 0x180436090 ================= */
/* name   = FUN_180436090 */
/* entry  = 180436090 */
/* body   = 23 bytes */
/* sig    = undefined FUN_180436090() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_180436090(int param_1)

{
  if (param_1 == -1) {
    return 0;
  }
  return *(undefined8 *)(_DAT_1881a3628 + (longlong)param_1 * 8);
}



/* ================= 0x180436120 ================= */
/* name   = FUN_180436120 */
/* entry  = 180436120 */
/* body   = 62 bytes */
/* sig    = undefined FUN_180436120() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_180436120(void)

{
  undefined8 uVar1;
  
  uVar1 = FUN_18042d650(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a1f18);
  uVar1 = FUN_1804457f0(uVar1);
  FUN_180446020(uVar1,0);
  return uVar1;
}



/* ================= 0x180442270 ================= */
/* name   = FUN_180442270 */
/* entry  = 180442270 */
/* body   = 18 bytes */
/* sig    = undefined FUN_180442270() */


undefined1 FUN_180442270(longlong param_1)

{
  if ((*(char *)(param_1 + 0x36) != '\0') && (*(char *)(param_1 + 0x37) == '\0')) {
    return 1;
  }
  return 0;
}



/* ================= 0x180430f20 ================= */
/* name   = FUN_180430f20 */
/* entry  = 180430f20 */
/* body   = 6 bytes */
/* sig    = undefined FUN_180430f20() */


void FUN_180430f20(void)

{
  LOCK();
  UNLOCK();
  return;
}



/* ================= 0x18043bd10 ================= */
/* name   = FUN_18043bd10 */
/* entry  = 18043bd10 */
/* body   = 382 bytes */
/* sig    = undefined FUN_18043bd10() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_18043bd10(undefined8 param_1)

{
  longlong lVar1;
  undefined8 uVar2;
  longlong lVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uStackX_8;
  undefined8 uVar6;
  longlong lStack_40;
  longlong lStack_38;
  undefined8 uStack_30;
  undefined1 uStack_28;
  
  uVar6 = 0xfffffffffffffffe;
  uVar4 = 0x1899db6d8;
  uVar5 = 0x1899db6d8;
  if (_DAT_18993b6d0 != 0) {
    uVar5 = 0x1899db6b8;
  }
  uStack_28 = 0;
  uStackX_8 = param_1;
  uStack_30 = uVar5;
  func_0x0001803f4a20(uVar5);
  lVar3 = _DAT_1899dbb38;
  uVar2 = func_0x0001804ea210(_DAT_1899dbb38 + 1,param_1);
  FUN_18041c590(lVar3,&lStack_40,&uStackX_8,uVar2,uVar6);
  if (((lStack_40 - *(longlong *)(lVar3 + 0x10) & 0xffffffffffffffe0U) + *(longlong *)(lVar3 + 0x10)
       == *(longlong *)(lVar3 + 0x18)) && (lStack_38 == 0)) {
    func_0x0001803f5a60(uVar5);
    lVar3 = FUN_1804457f0(_DAT_1899db358);
    *(undefined8 *)(lVar3 + 0x10) = param_1;
    if (_DAT_18993b6d0 != 0) {
      uVar4 = 0x1899db6b8;
    }
    uStack_28 = 1;
    uStack_30 = uVar4;
    func_0x0001803f4a10(uVar4);
    lVar1 = _DAT_1899dbb38;
    uVar5 = func_0x0001804ea210(_DAT_1899dbb38 + 1,param_1);
    FUN_18041c590(lVar1,&lStack_40,&uStackX_8,uVar5);
    if (((lStack_40 - *(longlong *)(lVar1 + 0x10) & 0xffffffffffffffe0U) +
         *(longlong *)(lVar1 + 0x10) == *(longlong *)(lVar1 + 0x18)) && (lStack_38 == 0)) {
      FUN_18042ab80(_DAT_1899dbb38,&uStackX_8,lVar3);
    }
    else {
      lVar3 = *(longlong *)(*(longlong *)(lVar1 + 0x60) + *(longlong *)(lStack_38 + 8) * 8);
    }
    func_0x0001803f5a50(uVar4);
  }
  else {
    lVar3 = *(longlong *)(*(longlong *)(lVar3 + 0x60) + *(longlong *)(lStack_38 + 8) * 8);
    func_0x0001803f5a60(uVar5);
  }
  return lVar3;
}



/* ================= 0x180430150 ================= */
/* name   = FUN_180430150 */
/* entry  = 180430150 */
/* body   = 55 bytes */
/* sig    = undefined FUN_180430150() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_180430150(longlong *param_1,char param_2)

{
  int iVar1;
  undefined4 *puVar2;
  code *pcVar3;
  longlong lVar4;
  longlong lVar5;
  char cVar6;
  undefined1 uVar7;
  undefined2 uVar8;
  undefined4 uVar9;
  longlong lVar10;
  longlong lVar11;
  longlong lVar12;
  undefined8 *puVar13;
  longlong lVar14;
  undefined8 uVar15;
  longlong *plVar16;
  ulonglong uVar17;
  uint uVar18;
  bool bVar19;
  longlong alStackX_8 [2];
  longlong lStack_98;
  longlong lStack_90;
  longlong lStack_80;
  uint uStack_78;
  undefined4 uStack_74;
  longlong lStack_70;
  longlong lStack_68;
  longlong lStack_60;
  longlong lStack_58;
  undefined8 uStack_50;
  undefined8 uStack_48;
  undefined *puStack_40;
  ulonglong in_stack_ffffffffffffffd0;
  ulonglong in_stack_ffffffffffffffe8;
  
  switch(*(undefined1 *)((longlong)param_1 + 10)) {
  case 1:
    return _DAT_1899db1d8;
  case 2:
    return _DAT_1899db1e0;
  case 3:
    return _DAT_1899db240;
  case 4:
    return _DAT_1899db1e8;
  case 5:
    return _DAT_1899db1d0;
  case 6:
    return _DAT_1899db1f0;
  case 7:
    return _DAT_1899db1f8;
  case 8:
    return _DAT_1899db200;
  case 9:
    return _DAT_1899db208;
  case 10:
    return _DAT_1899db220;
  case 0xb:
    return _DAT_1899db228;
  case 0xc:
    return _DAT_1899db230;
  case 0xd:
    return _DAT_1899db238;
  case 0xe:
    return _DAT_1899db248;
  case 0xf:
    puStack_40 = &UNK_180430295;
    lVar10 = FUN_180430150(*param_1,1);
    alStackX_8[1] = 0x1899db6b0;
    lStack_60 = 0x180439f20;
    func_0x0001803f4990(0x1899db6b0);
    lStack_60 = 0x180439f29;
    lVar14 = FUN_180439a90(lVar10);
    if (lVar14 == 0) {
      lStack_60 = 0x180439f4a;
      lVar14 = FUN_1804f09a0(_DAT_1899dbad0,1,0x148);
      if (lVar14 != 0) {
        lStack_60 = 0x180439f62;
        FUN_180500080(lVar14,0,0x148);
        *(undefined8 *)(lVar14 + 200) = 0;
        *(undefined8 *)(lVar14 + 0xd0) = 0;
      }
      *(longlong *)lVar14 = lVar14;
      *(undefined8 *)(lVar14 + 0x20) = *(undefined8 *)(lVar10 + 0x20);
      lStack_60 = 0x180439f9b;
      puVar13 = (undefined8 *)
                FUN_1804f17f0(&stack0xffffffffffffffd0,&UNK_1881a1cec,*(undefined8 *)(lVar10 + 0xa8)
                             );
      if (0xf < (ulonglong)puVar13[3]) {
        puVar13 = (undefined8 *)*puVar13;
      }
      lStack_60 = 0x180439fae;
      uVar15 = FUN_1804f30f0(puVar13);
      *(undefined8 *)(lVar14 + 0xa8) = uVar15;
      if (0xf < in_stack_ffffffffffffffe8) {
        uVar17 = in_stack_ffffffffffffffd0;
        if (0xfff < in_stack_ffffffffffffffe8 + 1) {
          if ((in_stack_ffffffffffffffd0 & 0x1f) != 0) {
            lStack_60 = 0x180439fda;
            FUN_180509dc8();
            pcVar3 = (code *)swi(3);
            lVar10 = (*pcVar3)();
            return lVar10;
          }
          uVar17 = *(ulonglong *)(in_stack_ffffffffffffffd0 - 8);
          if (in_stack_ffffffffffffffd0 <= uVar17) {
            lStack_60 = 0x180439fe9;
            FUN_180509dc8();
            pcVar3 = (code *)swi(3);
            lVar10 = (*pcVar3)();
            return lVar10;
          }
          if (in_stack_ffffffffffffffd0 - uVar17 < 8) {
            lStack_60 = 0x180439ff8;
            FUN_180509dc8();
            pcVar3 = (code *)swi(3);
            lVar10 = (*pcVar3)();
            return lVar10;
          }
          if (0x27 < in_stack_ffffffffffffffd0 - uVar17) {
            lStack_60 = 0x18043a004;
            FUN_180509dc8();
            pcVar3 = (code *)swi(3);
            lVar10 = (*pcVar3)();
            return lVar10;
          }
        }
        lStack_60 = 0x18043a00d;
        thunk_FUN_18050a3b8(uVar17);
      }
      *(undefined8 *)(lVar14 + 0x58) = *(undefined8 *)(lVar10 + 0x58);
      *(undefined1 *)(lVar14 + 0x13f) = 1;
      *(uint *)(lVar14 + 0x10c) = *(uint *)(lVar10 + 0x10c) & 7;
      *(undefined4 *)(lVar14 + 0x114) = 8;
      *(undefined1 *)(lVar14 + 0x6a) = 0xf;
      *(undefined1 *)(lVar14 + 0xba) = 0xf;
      *(longlong *)(lVar14 + 0x60) = lVar10 + 0x60;
      *(longlong *)(lVar14 + 0xb0) = lVar10 + 0x60;
      *(uint *)(lVar14 + 0xb8) = *(uint *)(lVar14 + 0xb8) | 0x40000000;
      *(undefined8 *)(lVar14 + 0x80) = 0;
      *(longlong *)(lVar14 + 0x30) = lVar10;
      *(longlong *)(lVar14 + 0x98) = lVar10;
      lStack_60 = 0x18043a07b;
      FUN_18042bac0(lVar10,lVar14);
    }
    lStack_60 = 0x18043a084;
    func_0x0001803f72c0(0x1899db6b0);
    return lVar14;
  default:
    return 0;
  case 0x11:
  case 0x12:
    iVar1 = (int)*param_1;
    if (iVar1 == -1) {
      lVar10 = 0;
    }
    else {
      lVar10 = (longlong)iVar1 * 8;
      if (*(longlong *)(lVar10 + _DAT_1899dbbf0) == 0) {
        alStackX_8[1] = 0x1899db6b0;
        puStack_40 = (undefined *)0x18043b36f;
        func_0x0001803f4990(0x1899db6b0);
        if (*(longlong *)(lVar10 + _DAT_1899dbbf0) == 0) {
          puStack_40 = (undefined *)0x18043b385;
          uVar15 = FUN_180430980(iVar1);
          *(undefined8 *)(lVar10 + _DAT_1899dbbf0) = uVar15;
        }
        puStack_40 = (undefined *)0x18043b398;
        func_0x0001803f72c0(0x1899db6b0);
      }
      lVar10 = *(longlong *)(lVar10 + _DAT_1899dbbf0);
    }
    return lVar10;
  case 0x13:
  case 0x1e:
    puStack_40 = &UNK_180430351;
    lVar10 = FUN_18042fe20(&stack0xffffffffffffffe8);
    return lVar10;
  case 0x14:
    puStack_40 = &UNK_180430274;
    lVar10 = FUN_180430150(*(undefined8 *)*param_1);
    bVar19 = true;
    uVar17 = (ulonglong)*(byte *)(*param_1 + 8);
    break;
  case 0x15:
    puVar2 = (undefined4 *)*param_1;
    lStack_60 = 0x180432a9a;
    func_0x0001803f4990(0x1899db6b0);
    lStack_60 = 0x180432aa2;
    lVar10 = FUN_18043b320(*puVar2);
    if (lVar10 == 0) {
      if (param_2 != '\0') {
        lStack_60 = 0x180432acf;
        lVar10 = FUN_1804303f0(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a2068,&UNK_1881a2220);
        lStack_60 = 0x180432adc;
        FUN_180447cf0(lVar10,0);
        lStack_60 = 0x180432af2;
        alStackX_8[0] = lVar10;
        FUN_1804ff8e0(alStackX_8,&UNK_188d08588);
      }
      lStack_60 = 0x180432afb;
      func_0x0001803f72c0(0x1899db6b0);
      lVar10 = 0;
    }
    else {
      if (*(longlong *)(puVar2 + 6) == 0) {
        lStack_60 = 0x180432b32;
        lVar14 = FUN_1804f09a0(_DAT_1899dbad0,1,
                               (ulonglong)*(ushort *)(lVar10 + 0x120) * 0x10 + 0x148);
        if (lVar14 != 0) {
          lStack_60 = 0x180432b4d;
          FUN_180500080(lVar14,0,0x148);
          *(undefined8 *)(lVar14 + 200) = 0;
          *(undefined8 *)(lVar14 + 0xd0) = 0;
        }
        *(longlong *)(puVar2 + 6) = lVar14;
        *(longlong *)lVar14 = lVar14;
        *(undefined8 *)(lVar14 + 0xa8) = *(undefined8 *)(lVar10 + 0xa8);
        *(undefined8 *)(lVar14 + 0x20) = *(undefined8 *)(lVar10 + 0x20);
        *(undefined8 *)(lVar14 + 0x58) = *(undefined8 *)(lVar10 + 0x58);
        *(undefined4 *)(lVar14 + 0x10c) = *(undefined4 *)(lVar10 + 0x10c);
        *(undefined4 **)(lVar14 + 0xc0) = puVar2;
        lStack_60 = 0x180432b9a;
        lVar11 = FUN_18043b320(*puVar2);
        lVar12 = *(longlong *)(lVar14 + 0xc0);
        if (*(longlong *)(lVar11 + 0x80) != 0) {
          lStack_60 = 0x180432bc0;
          uVar15 = FUN_1804ecb50(*(longlong *)(lVar11 + 0x80) + 0x60,lVar12 + 8,0);
          lStack_60 = 0x180432bca;
          uVar15 = FUN_180430150(uVar15,1);
          *(undefined8 *)(lVar14 + 0x80) = uVar15;
        }
        if (*(longlong *)(lVar11 + 0x88) != 0) {
          lStack_60 = 0x180432bed;
          uVar15 = FUN_1804ecb50(*(longlong *)(lVar11 + 0x88) + 0x60,lVar12 + 8,0);
          lStack_60 = 0x180432bf7;
          uVar15 = FUN_180430150(uVar15,1);
          *(undefined8 *)(lVar14 + 0x88) = uVar15;
        }
        *(undefined1 *)(lVar14 + 0x6a) = 0x15;
        *(undefined1 *)(lVar14 + 0xba) = 0x15;
        *(undefined4 **)(lVar14 + 0x60) = puVar2;
        *(undefined4 **)(lVar14 + 0xb0) = puVar2;
        *(uint *)(lVar14 + 0xb8) = *(uint *)(lVar14 + 0xb8) | 0x40000000;
        *(undefined2 *)(lVar14 + 0x128) = *(undefined2 *)(lVar10 + 0x128);
        *(undefined2 *)(lVar14 + 0x12a) = *(undefined2 *)(lVar10 + 0x12a);
        *(undefined2 *)(lVar14 + 300) = *(undefined2 *)(lVar10 + 300);
        *(undefined2 *)(lVar14 + 0x124) = *(undefined2 *)(lVar10 + 0x124);
        *(undefined2 *)(lVar14 + 0x126) = *(undefined2 *)(lVar10 + 0x126);
        *(undefined1 *)(lVar14 + 0x137) = *(undefined1 *)(lVar10 + 0x137);
        *(undefined1 *)(lVar14 + 0x142) = *(undefined1 *)(lVar10 + 0x142);
        *(longlong *)(lVar14 + 0x98) = lVar14;
        *(longlong *)(lVar14 + 0x30) = lVar14;
        cVar6 = *(char *)(lVar10 + 0x139);
        *(char *)(lVar14 + 0x139) = cVar6;
        *(uint *)(lVar14 + 0xe8) = (uint)(cVar6 == '\0');
        *(undefined1 *)(lVar14 + 0x13b) = *(undefined1 *)(lVar10 + 0x13b);
        *(undefined4 *)(lVar14 + 0x118) = 0xffffffff;
        *(undefined4 *)(lVar14 + 0x100) = 0xffffffff;
        *(undefined4 *)(lVar14 + 0xf8) = *(undefined4 *)(lVar10 + 0xf8);
        lStack_60 = 0x180432cd8;
        uVar15 = FUN_180436810();
        *(undefined8 *)(lVar14 + 0x48) = uVar15;
        if (*(undefined4 **)(lVar14 + 0xc0) != (undefined4 *)0x0) {
          lStack_60 = 0x180432cef;
          lVar12 = FUN_18043b320(**(undefined4 **)(lVar14 + 0xc0));
          if (lVar12 == _DAT_1899db360) {
            lStack_60 = 0x180432d11;
            uVar15 = FUN_180430150(**(undefined8 **)
                                     (*(longlong *)(*(longlong *)(lVar14 + 0xc0) + 8) + 8),1);
            *(undefined8 *)(lVar14 + 0x98) = uVar15;
            *(undefined8 *)(lVar14 + 0x30) = uVar15;
          }
        }
        if (*(char *)(lVar14 + 0x137) != '\0') {
          uVar15 = *(undefined8 *)(lVar10 + 0x30);
          *(undefined8 *)(lVar14 + 0x98) = uVar15;
          *(undefined8 *)(lVar14 + 0x30) = uVar15;
        }
        *(undefined1 *)(lVar14 + 0x141) = *(undefined1 *)(lVar10 + 0x141);
      }
      lVar10 = *(longlong *)(puVar2 + 6);
      lStack_60 = 0x180432d4d;
      func_0x0001803f72c0(0x1899db6b0);
    }
    return lVar10;
  case 0x16:
    return _DAT_1899db320;
  case 0x18:
    return _DAT_1899db210;
  case 0x19:
    return _DAT_1899db218;
  case 0x1c:
    return _DAT_1899db1c8;
  case 0x1d:
    puStack_40 = &UNK_1804302aa;
    lVar10 = FUN_180430150(*param_1);
    bVar19 = false;
    uVar17 = 1;
  }
  uStack_50 = 0xfffffffffffffffe;
  uStack_48 = 0x1899db6b0;
  alStackX_8[0] = lVar10;
  func_0x0001803f4990(0x1899db6b0);
  uVar18 = (uint)uVar17;
  if (uVar18 < 2) {
    if (bVar19) goto LAB_1804eb78a;
    uVar15 = FUN_1804ec590(lVar10 + 0x60);
    FUN_1804e7a60(0x1899ddf80,&lStack_98,alStackX_8,uVar15);
    if (((lStack_98 - _DAT_1899ddf90 & 0xffffffffffffffe0U) + _DAT_1899ddf90 != _DAT_1899ddf98) ||
       (lStack_90 != 0)) {
      lVar14 = *(longlong *)(lStack_90 + 8);
      goto LAB_1804ebaa8;
    }
  }
  else {
    bVar19 = false;
LAB_1804eb78a:
    lStack_90 = CONCAT44(lStack_90._4_4_,uVar18);
    lStack_98 = lVar10;
    lVar14 = FUN_1804ec590(lVar10 + 0x60);
    FUN_1804e7d60(0x1899ddfe0,&lStack_80,&lStack_98,lVar14 * uVar17);
    if (((lStack_80 - _DAT_1899ddff0 & 0xffffffffffffffe0U) + _DAT_1899ddff0 != _DAT_1899ddff8) ||
       (CONCAT44(uStack_74,uStack_78) != 0)) {
      lVar14 = *(longlong *)(CONCAT44(uStack_74,uStack_78) + 0x10);
      goto LAB_1804ebaa8;
    }
  }
  lVar12 = _DAT_1899db258;
  lVar11 = lVar10 + 0x60;
  FUN_18043d300(_DAT_1899db258);
  lStack_68 = 0;
  lStack_60 = 0;
  lStack_58 = 0;
  if ((uVar18 < 2) && (!bVar19)) {
    FUN_1804ea7e0(lVar10,&lStack_68);
  }
  lVar5 = lStack_58;
  lVar4 = lStack_68;
  lVar14 = lStack_60 - lStack_68 >> 3;
  lStack_98 = ((ulonglong)*(ushort *)(_DAT_1899db340 + 0x124) +
               (ulonglong)*(ushort *)(_DAT_1899db338 + 0x124) +
              (ulonglong)*(ushort *)(_DAT_1899db330 + 0x124)) * lVar14 +
              ((ulonglong)*(ushort *)(_DAT_1899db350 + 0x124) +
              (ulonglong)*(ushort *)(_DAT_1899db348 + 0x124)) * lVar14 +
              (ulonglong)*(ushort *)(lVar12 + 0x120);
  lVar14 = func_0x000180440bd0(1,lStack_98 * 0x10 + 0x148);
  if (lVar14 != 0) {
    FUN_180500080(lVar14,0,0x148);
    *(undefined8 *)(lVar14 + 200) = 0;
    *(undefined8 *)(lVar14 + 0xd0) = 0;
  }
  *(longlong *)lVar14 = lVar14;
  *(undefined8 *)(lVar14 + 0x58) = *(undefined8 *)(lVar10 + 0x58);
  *(undefined8 *)(lVar14 + 0x20) = *(undefined8 *)(lVar10 + 0x20);
  uVar15 = FUN_1804eb580(*(undefined8 *)(lVar10 + 0xa8),uVar17);
  *(undefined8 *)(lVar14 + 0xa8) = uVar15;
  *(longlong *)(lVar14 + 0x80) = _DAT_1899db258;
  *(undefined4 *)(lVar14 + 0x10c) = 0x2101;
  *(char *)(lVar14 + 0x131) = (char)uVar17;
  uVar9 = func_0x0001804363b0(lVar12);
  *(undefined4 *)(lVar14 + 0x114) = uVar9;
  *(undefined1 *)(lVar14 + 0x138) = 1;
  *(short *)(lVar14 + 0x120) = (short)lStack_98;
  FUN_18044b5c0(lVar10);
  uVar9 = FUN_180431e40(lVar10);
  *(undefined4 *)(lVar14 + 0xfc) = uVar9;
  *(undefined4 *)(lVar14 + 0x118) = 0xffffffff;
  *(undefined4 *)(lVar14 + 0x100) = 0xffffffff;
  cVar6 = FUN_180442500(lVar11);
  if ((cVar6 == '\0') && (*(char *)(lVar10 + 0x13a) == '\0')) {
    uVar7 = 0;
  }
  else {
    uVar7 = 1;
  }
  *(undefined1 *)(lVar14 + 0x13a) = uVar7;
  *(longlong *)(lVar14 + 0x30) = lVar10;
  if ((1 < uVar18) || (bVar19)) {
    plVar16 = (longlong *)func_0x000180440bd0();
    if (plVar16 != (longlong *)0x0) {
      *plVar16 = 0;
      plVar16[1] = 0;
      plVar16[2] = 0;
      plVar16[3] = 0;
    }
    *(undefined1 *)(lVar14 + 0x6a) = 0x14;
    *(longlong **)(lVar14 + 0x60) = plVar16;
    *plVar16 = lVar11;
    *(char *)(plVar16 + 1) = (char)uVar17;
  }
  else {
    *(undefined1 *)(lVar14 + 0x6a) = 0x1d;
    *(longlong *)(lVar14 + 0x60) = lVar11;
  }
  *(undefined4 *)(lVar14 + 0xb0) = *(undefined4 *)(lVar14 + 0x60);
  *(undefined4 *)(lVar14 + 0xb4) = *(undefined4 *)(lVar14 + 100);
  *(undefined4 *)(lVar14 + 0xb8) = *(undefined4 *)(lVar14 + 0x68);
  *(undefined4 *)(lVar14 + 0xbc) = *(undefined4 *)(lVar14 + 0x6c);
  *(uint *)(lVar14 + 0xb8) = *(uint *)(lVar14 + 0xb8) | 0x40000000;
  if ((1 < uVar18) || (bVar19)) {
    uVar8 = 0;
  }
  else {
    uVar8 = 5;
  }
  *(undefined2 *)(lVar14 + 300) = uVar8;
  uVar15 = FUN_180436810();
  *(undefined8 *)(lVar14 + 0x48) = uVar15;
  if ((1 < uVar18) || (bVar19)) {
    lStack_80 = *(longlong *)(lVar14 + 0x30);
    uStack_78 = (uint)*(byte *)(lVar14 + 0x131);
    lStack_70 = lVar14;
    FUN_1804e86e0(0x1899ddfe0,&lStack_98,&lStack_80,&lStack_80);
  }
  else {
    lStack_98 = *(longlong *)(lVar14 + 0x30);
    lStack_90 = lVar14;
    FUN_1804e8af0(0x1899ddf80,&lStack_80,&lStack_98,&lStack_98);
  }
  if (lVar4 != 0) {
    FUN_180452930(&lStack_68,lVar4,lVar5 - lVar4 >> 3);
  }
LAB_1804ebaa8:
  func_0x0001803f72c0(0x1899db6b0);
  return lVar14;
}



/* ================= 0x18042c350 ================= */
/* name   = FUN_18042c350 */
/* entry  = 18042c350 */
/* body   = 441 bytes */
/* sig    = undefined FUN_18042c350() */


longlong FUN_18042c350(longlong param_1,undefined8 param_2)

{
  code *pcVar1;
  char cVar2;
  undefined8 uVar3;
  longlong lVar4;
  undefined1 *puVar5;
  undefined8 ****ppppuVar6;
  undefined8 ***apppuStack_1c8 [2];
  longlong lStack_1b8;
  ulonglong uStack_1b0;
  undefined1 uStack_1a8;
  undefined7 uStack_1a7;
  undefined8 uStack_198;
  ulonglong uStack_190;
  undefined1 *puStack_188;
  undefined2 uStack_180;
  undefined8 ***pppuStack_178;
  longlong lStack_170;
  undefined8 uStack_168;
  undefined1 auStack_160 [32];
  undefined1 auStack_140 [40];
  undefined1 auStack_118 [80];
  longlong lStack_c8;
  
  uStack_168 = 0xfffffffffffffffe;
  if (param_1 != 0) {
    uVar3 = func_0x0001804f1130();
    FUN_1804f3320(apppuStack_1c8,uVar3);
    FUN_1804293c0(auStack_118);
    puStack_188 = auStack_118;
    uStack_180 = 0x100;
    pppuStack_178 = apppuStack_1c8;
    if (0xf < uStack_1b0) {
      pppuStack_178 = apppuStack_1c8[0];
    }
    lStack_170 = (longlong)pppuStack_178 + lStack_1b8;
    cVar2 = FUN_180446930(&puStack_188,1);
    if ((cVar2 == '\0') || (lStack_c8 != 0)) {
      FUN_18042a8b0(auStack_118);
      if (0xf < uStack_1b0) {
        ppppuVar6 = (undefined8 ****)apppuStack_1c8[0];
        if (0xfff < uStack_1b0 + 1) {
          if (((ulonglong)apppuStack_1c8[0] & 0x1f) != 0) {
            FUN_180509dc8();
            pcVar1 = (code *)swi(3);
            lVar4 = (*pcVar1)();
            return lVar4;
          }
          ppppuVar6 = (undefined8 ****)apppuStack_1c8[0][-1];
          if (apppuStack_1c8[0] <= ppppuVar6) {
            FUN_180509dc8();
            pcVar1 = (code *)swi(3);
            lVar4 = (*pcVar1)();
            return lVar4;
          }
          if ((ulonglong)((longlong)apppuStack_1c8[0] - (longlong)ppppuVar6) < 8) {
            FUN_180509dc8();
            pcVar1 = (code *)swi(3);
            lVar4 = (*pcVar1)();
            return lVar4;
          }
          if (0x27 < (ulonglong)((longlong)apppuStack_1c8[0] - (longlong)ppppuVar6)) {
            FUN_180509dc8();
            pcVar1 = (code *)swi(3);
            lVar4 = (*pcVar1)();
            return lVar4;
          }
        }
        thunk_FUN_18050a3b8(ppppuVar6);
      }
    }
    else {
      uStack_190 = 0xf;
      uStack_198 = 0;
      uStack_1a8 = 0;
      uVar3 = FUN_1804172e0(auStack_140,apppuStack_1c8,&UNK_188195204);
      uVar3 = FUN_1803fabc0(auStack_160,uVar3,param_2);
      FUN_1803f01c0(&uStack_1a8,uVar3);
      FUN_1803ed580(auStack_160);
      FUN_1803ed580(auStack_140);
      puVar5 = &uStack_1a8;
      if (0xf < uStack_190) {
        puVar5 = (undefined1 *)CONCAT71(uStack_1a7,uStack_1a8);
      }
      param_1 = FUN_180445770(puVar5);
      FUN_1803ed580(&uStack_1a8);
      FUN_18042a8b0(auStack_118);
      FUN_1803ed580(apppuStack_1c8);
    }
  }
  return param_1;
}



/* ================= 0x18042eab0 ================= */
/* name   = FUN_18042eab0 */
/* entry  = 18042eab0 */
/* body   = 250 bytes */
/* sig    = undefined FUN_18042eab0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_18042eab0(longlong param_1,longlong param_2,undefined8 param_3,undefined8 param_4)

{
  byte bVar1;
  undefined8 *puVar2;
  undefined8 *puVar3;
  longlong lVar4;
  ulonglong uVar5;
  undefined8 uVar6;
  ulonglong uVar7;
  
  uVar6 = 0xfffffffffffffffe;
  bVar1 = *(byte *)(*(longlong *)(param_1 + 0x28) + 0x32);
  uVar5 = (ulonglong)(bVar1 + 2);
  uVar7 = uVar5;
  puVar2 = (undefined8 *)func_0x0001804f0770((bVar1 + 2) * 8);
  lVar4 = 0;
  if (bVar1 != 0) {
    puVar3 = puVar2;
    do {
      *puVar3 = *(undefined8 *)((param_2 - (longlong)puVar2) + (longlong)puVar3);
      lVar4 = lVar4 + 1;
      puVar3 = puVar3 + 1;
    } while (lVar4 < (longlong)(ulonglong)bVar1);
  }
  puVar2[bVar1] = param_3;
  puVar2[bVar1 + 1] = param_4;
  puVar3 = puVar2;
  if (_DAT_1899dbb98 == 0) {
    _DAT_1899dbb98 = thunk_FUN_1804df2c0(0x30,0);
  }
  uVar6 = FUN_1804f8170(_DAT_1899dbb98,param_1,*(undefined8 *)(param_1 + 0x28),puVar2,uVar6,puVar3,
                        uVar5,uVar7);
  func_0x0001804f0760(puVar2);
  return uVar6;
}



/* ================= 0x18042ebb0 ================= */
/* name   = FUN_18042ebb0 */
/* entry  = 18042ebb0 */
/* body   = 271 bytes */
/* sig    = undefined FUN_18042ebb0() */


undefined8 FUN_18042ebb0(longlong param_1,undefined8 *param_2)

{
  longlong lVar1;
  code *pcVar2;
  undefined8 uVar3;
  longlong lVar4;
  longlong *plVar5;
  longlong *plVar6;
  longlong lVar7;
  longlong lStackX_18;
  longlong lStackX_20;
  
  uVar3 = FUN_1804f8320(param_1,&lStackX_20,&lStackX_18);
  if (lStackX_18 != 0) {
    func_0x0001803ede90();
    pcVar2 = (code *)swi(3);
    uVar3 = (*pcVar2)();
    return uVar3;
  }
  if (param_2 != (undefined8 *)0x0) {
    plVar5 = (longlong *)0x0;
    lVar1 = *(longlong *)(*(longlong *)(param_1 + 0x20) + 0x28);
    if (((*(longlong *)(lVar1 + 0x40) == 0) ||
        (plVar6 = (longlong *)(*(longlong *)(*(longlong *)(lVar1 + 0x40) + 8) + -0x17c6f466730c70a9)
        , plVar6 == (longlong *)0x0)) && (plVar6 = plVar5, *(char *)(lVar1 + 0x32) != '\0')) {
      plVar6 = (longlong *)FUN_180437600(lVar1);
    }
    if (*(char *)(lVar1 + 0x32) != '\0') {
      lVar7 = (lStackX_20 + 0x20) - (longlong)param_2;
      do {
        if ((*(uint *)(*plVar6 + 8) & 0x40000000) != 0) {
          lVar4 = thunk_FUN_180430150();
          if (*(char *)(lVar4 + 0x142) == '\0') {
            *(undefined8 *)*param_2 = *(undefined8 *)(lVar7 + (longlong)param_2);
          }
          else {
            FUN_180500230((undefined8 *)*param_2,*(longlong *)(lVar7 + (longlong)param_2) + 0x10,
                          (longlong)*(int *)(lVar4 + 0x100));
          }
          param_2 = param_2 + 1;
        }
        plVar5 = (longlong *)((longlong)plVar5 + 1);
        plVar6 = plVar6 + 3;
      } while (plVar5 < (longlong *)(ulonglong)*(byte *)(lVar1 + 0x32));
    }
  }
  return uVar3;
}



/* ================= 0x1804318e0 ================= */
/* name   = FUN_1804318e0 */
/* entry  = 1804318e0 */
/* body   = 419 bytes */
/* sig    = undefined FUN_1804318e0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_1804318e0(longlong param_1,undefined8 param_2)

{
  code *pcVar1;
  longlong lVar2;
  undefined8 *puVar3;
  undefined8 uVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  int iVar7;
  byte *pbVar8;
  byte bStack_30;
  undefined1 uStack_2f;
  undefined6 uStack_2e;
  ulonglong uStack_20;
  ulonglong uStack_18;
  
  lVar2 = FUN_1804303f0(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a1e90,param_2,0xfffffffffffffffe);
  if (param_1 != 0) {
    uVar6 = 0xffffffffffffffff;
    do {
      uVar6 = uVar6 + 1;
    } while (*(char *)(param_1 + uVar6) != '\0');
    FUN_1804f3430(&bStack_30,param_1,uVar6 & 0xffffffff);
    pbVar8 = &bStack_30;
    if (7 < uStack_18) {
      pbVar8 = (byte *)CONCAT62(uStack_2e,CONCAT11(uStack_2f,bStack_30));
    }
    iVar7 = (int)uStack_20;
    puVar3 = _DAT_1899dbb50;
    if (iVar7 != 0) {
      if ((longlong)(iVar7 * 2 + 2) + 0x18U < (uStack_20 & 0xffffffff)) {
        FUN_1804489d0();
        pcVar1 = (code *)swi(3);
        lVar2 = (*pcVar1)();
        return lVar2;
      }
      puVar3 = (undefined8 *)func_0x0001804df180();
      *puVar3 = _DAT_1899db248;
      puVar3[1] = 0;
      *(int *)(puVar3 + 2) = iVar7;
      *(undefined2 *)((longlong)puVar3 + (longlong)iVar7 * 2 + 0x14) = 0;
    }
    uVar4 = func_0x0001804f1130(puVar3);
    FUN_180500230(uVar4,pbVar8,(longlong)(iVar7 * 2));
    if (7 < uStack_18) {
      uVar6 = CONCAT62(uStack_2e,CONCAT11(uStack_2f,bStack_30));
      if (0x7fffffffffffffff < uStack_18 + 1) {
        FUN_180509dc8();
        pcVar1 = (code *)swi(3);
        lVar2 = (*pcVar1)();
        return lVar2;
      }
      uVar5 = uVar6;
      if (0xfff < (uStack_18 + 1) * 2) {
        if ((bStack_30 & 0x1f) != 0) {
          FUN_180509dc8();
          pcVar1 = (code *)swi(3);
          lVar2 = (*pcVar1)();
          return lVar2;
        }
        uVar5 = *(ulonglong *)(uVar6 - 8);
        if (uVar6 <= uVar5) {
          FUN_180509dc8();
          pcVar1 = (code *)swi(3);
          lVar2 = (*pcVar1)();
          return lVar2;
        }
        if (uVar6 - uVar5 < 8) {
          FUN_180509dc8();
          pcVar1 = (code *)swi(3);
          lVar2 = (*pcVar1)();
          return lVar2;
        }
        if (0x27 < uVar6 - uVar5) {
          FUN_180509dc8();
          pcVar1 = (code *)swi(3);
          lVar2 = (*pcVar1)();
          return lVar2;
        }
      }
      thunk_FUN_18050a3b8(uVar5);
    }
    uStack_18 = 7;
    uStack_20 = 0;
    bStack_30 = 0;
    uStack_2f = 0;
    func_0x0001803edc70(lVar2,lVar2 + 0x88,puVar3);
  }
  return lVar2;
}



/* ================= 0x180435fb0 ================= */
/* name   = FUN_180435fb0 */
/* entry  = 180435fb0 */
/* body   = 112 bytes */
/* sig    = undefined FUN_180435fb0() */


void FUN_180435fb0(longlong param_1,longlong param_2,undefined8 param_3,undefined8 param_4)

{
  undefined4 uVar1;
  undefined8 uVar2;
  longlong lVar3;
  undefined8 *puVar4;
  undefined1 auStack_30 [40];
  
  uVar2 = 0;
  if (*(char *)(param_1 + 0x36) == '\0') {
    uVar1 = *(undefined4 *)(param_1 + 0x18);
  }
  else {
    uVar2 = *(undefined8 *)(*(undefined4 **)(param_1 + 0x20) + 2);
    uVar1 = **(undefined4 **)(param_1 + 0x20);
  }
  uVar2 = FUN_180435c60(uVar1,uVar2,*(undefined8 *)(*(longlong *)(param_2 + 0x20) + 0x10),param_4,
                        0xfffffffffffffffe);
  lVar3 = FUN_1804ebea0(uVar2,0);
  if (*(longlong *)(lVar3 + 8) == 0) {
    puVar4 = (undefined8 *)FUN_1804ebae0(auStack_30,uVar2);
    if (0xf < (ulonglong)puVar4[3]) {
      puVar4 = (undefined8 *)*puVar4;
    }
    FUN_1804488a0(puVar4);
  }
  return;
}



/* ================= 0x180436cb0 ================= */
/* name   = FUN_180436cb0 */
/* entry  = 180436cb0 */
/* body   = 29 bytes */
/* sig    = undefined FUN_180436cb0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_180436cb0(longlong param_1)

{
  undefined2 *puVar1;
  undefined8 uVar2;
  undefined2 *puStack_60;
  undefined8 uStack_58;
  ulonglong uStack_48;
  undefined2 uStack_40;
  undefined6 uStack_3e;
  undefined8 uStack_30;
  ulonglong uStack_28;
  
  uVar2 = _DAT_1899db1c0;
  uStack_28 = 7;
  uStack_30 = 0;
  uStack_40 = 0;
  if (param_1 != 0) {
    puVar1 = (undefined2 *)
             FUN_1804f3400(&puStack_60,param_1,&UNK_1881a2198,param_1,0xfffffffffffffffe);
    if (&uStack_40 != puVar1) {
      if (7 < uStack_28) {
        FUN_1803f9830(&uStack_40,CONCAT62(uStack_3e,uStack_40),uStack_28 + 1);
      }
      uStack_28 = 7;
      uStack_30 = 0;
      uStack_40 = 0;
      FUN_1803f7f60(&uStack_40,puVar1);
    }
    if (7 < uStack_48) {
      FUN_1803f9830(&puStack_60,puStack_60,uStack_48 + 1);
    }
    puStack_60 = (undefined2 *)CONCAT62(uStack_3e,uStack_40);
    if (7 < uStack_28) goto LAB_1804304af;
  }
  puStack_60 = &uStack_40;
LAB_1804304af:
  uStack_58 = uStack_30;
  uVar2 = FUN_180430510(uVar2,&UNK_188195170,&UNK_1881a2198,&puStack_60);
  if (7 < uStack_28) {
    FUN_1803f9830(&uStack_40,CONCAT62(uStack_3e,uStack_40),uStack_28 + 1);
  }
  return uVar2;
}



/* ================= 0x180437a00 ================= */
/* name   = FUN_180437a00 */
/* entry  = 180437a00 */
/* body   = 29 bytes */
/* sig    = undefined FUN_180437a00() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_180437a00(longlong param_1)

{
  undefined2 *puVar1;
  undefined8 uVar2;
  undefined2 *puStack_60;
  undefined8 uStack_58;
  ulonglong uStack_48;
  undefined2 uStack_40;
  undefined6 uStack_3e;
  undefined8 uStack_30;
  ulonglong uStack_28;
  
  uVar2 = _DAT_1899db1c0;
  uStack_28 = 7;
  uStack_30 = 0;
  uStack_40 = 0;
  if (param_1 != 0) {
    puVar1 = (undefined2 *)
             FUN_1804f3400(&puStack_60,param_1,&UNK_1881a2180,param_1,0xfffffffffffffffe);
    if (&uStack_40 != puVar1) {
      if (7 < uStack_28) {
        FUN_1803f9830(&uStack_40,CONCAT62(uStack_3e,uStack_40),uStack_28 + 1);
      }
      uStack_28 = 7;
      uStack_30 = 0;
      uStack_40 = 0;
      FUN_1803f7f60(&uStack_40,puVar1);
    }
    if (7 < uStack_48) {
      FUN_1803f9830(&puStack_60,puStack_60,uStack_48 + 1);
    }
    puStack_60 = (undefined2 *)CONCAT62(uStack_3e,uStack_40);
    if (7 < uStack_28) goto LAB_1804304af;
  }
  puStack_60 = &uStack_40;
LAB_1804304af:
  uStack_58 = uStack_30;
  uVar2 = FUN_180430510(uVar2,&UNK_1881a1de8,&UNK_1881a2180,&puStack_60);
  if (7 < uStack_28) {
    FUN_1803f9830(&uStack_40,CONCAT62(uStack_3e,uStack_40),uStack_28 + 1);
  }
  return uVar2;
}



/* ================= 0x18042da80 ================= */
/* name   = FUN_18042da80 */
/* entry  = 18042da80 */
/* body   = 365 bytes */
/* sig    = undefined FUN_18042da80() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_18042da80(longlong *param_1)

{
  longlong *plVar1;
  longlong lVar2;
  longlong *plVar3;
  longlong lVar4;
  longlong lStack_20;
  longlong lStack_18;
  
  if (*(char *)(*param_1 + 0x141) != '\0') {
    func_0x0001803f4990(0x1899dba30);
    FUN_18041c4c0(0x1899db9b0,&lStack_20,param_1 + 2,param_1[2]);
    plVar3 = (longlong *)((lStack_20 - _DAT_1899db9c0 & 0xffffffffffffffe0U) + _DAT_1899db9c0);
    if (((plVar3 != _DAT_1899db9c8) || (lStack_18 != 0)) &&
       ((plVar1 = (longlong *)FUN_1804fb2f0(*(undefined4 *)(lStack_18 + 8)),
        plVar1 == (longlong *)0x0 || (plVar1 == param_1)))) {
      lVar2 = func_0x000180452b10(plVar3,0x1899db9b0,lStack_18);
      _DAT_1899db9e8 = _DAT_1899db9e8 + -1;
      _DAT_1899db9f0 = _DAT_1899db9f0 + 1;
      if (lVar2 == (ulonglong)*(byte *)(plVar3 + 3) * 0x10 + *plVar3) {
        do {
          if (plVar3 + 4 == _DAT_1899db9c8) break;
          plVar1 = plVar3 + 7;
          plVar3 = plVar3 + 4;
        } while ((char)*plVar1 == '\0');
      }
    }
    func_0x0001803f72c0(0x1899dba30);
  }
  lVar2 = (longlong)(int)param_1[0x14];
  if (0 < lVar2) {
    plVar3 = param_1 + 4;
    do {
      (**(code **)(*(longlong *)*plVar3 + 0x10))();
      plVar3 = plVar3 + 2;
      lVar2 = lVar2 + -1;
    } while (lVar2 != 0);
  }
  lVar2 = (longlong)*(int *)((longlong)param_1 + 0xa4);
  if (0 < *(int *)((longlong)param_1 + 0xa4)) {
    lVar4 = 0;
    do {
      (**(code **)(**(longlong **)(lVar4 + 8 + param_1[0x13]) + 0x10))();
      lVar4 = lVar4 + 0x10;
      lVar2 = lVar2 + -1;
    } while (lVar2 != 0);
    func_0x0001804f1110(param_1[0x13]);
  }
  return;
}



/* ================= 0x1804449b0 ================= */
/* name   = FUN_1804449b0 */
/* entry  = 1804449b0 */
/* body   = 40 bytes */
/* sig    = undefined FUN_1804449b0() */


undefined8 FUN_1804449b0(longlong param_1)

{
  longlong *plVar1;
  undefined8 uVar2;
  longlong lVar3;
  
  lVar3 = 0;
  if (param_1 == 0) {
    return 0;
  }
  do {
    plVar1 = (longlong *)(param_1 + 0x10);
    param_1 = *(longlong *)(param_1 + 0x18);
    lVar3 = lVar3 + *(longlong *)(*plVar1 + 0x18);
  } while (param_1 != 0);
                    /* WARNING: Could not recover jumptable at 0x0001803f0900. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  uVar2 = CoTaskMemAlloc(lVar3 * 2 + 2);
  return uVar2;
}



/* ================= 0x180444a40 ================= */
/* name   = FUN_180444a40 */
/* entry  = 180444a40 */
/* body   = 592 bytes */
/* sig    = undefined FUN_180444a40() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_180444a40(undefined8 param_1,longlong param_2)

{
  longlong lVar1;
  code *pcVar2;
  char cVar3;
  undefined8 uVar4;
  undefined8 *puVar5;
  longlong lVar6;
  undefined8 uStackX_18;
  undefined1 auStack_40 [40];
  
  cVar3 = FUN_18043d050(param_2,_DAT_1899db260);
  if (cVar3 == '\0') {
    uVar4 = FUN_1804318e0(&UNK_188195548,&UNK_1881a27a8);
    FUN_180447cf0(uVar4,0);
    uStackX_18 = uVar4;
    FUN_1804ff8e0(&uStackX_18,&UNK_188d08588);
    pcVar2 = (code *)swi(3);
    uVar4 = (*pcVar2)();
    return uVar4;
  }
  if ((*(char *)(param_2 + 0x13e) == '\0') && (*(longlong *)(param_2 + 0xc0) == 0)) {
    if ((*(longlong **)(param_2 + 0x48) != (longlong *)0x0) &&
       (lVar1 = **(longlong **)(param_2 + 0x48), lVar1 != 0)) {
      uVar4 = FUN_1804457f0(param_2);
      puVar5 = (undefined8 *)FUN_1804fd810(param_1);
      if (puVar5 == (undefined8 *)0x0) {
        lVar6 = FUN_180436f50(param_2,&UNK_1881a2e9c,0xffffffff,0,0);
        uStackX_18 = 0x1899db6b0;
        func_0x0001803f4990(0x1899db6b0);
        puVar5 = (undefined8 *)FUN_1804f09a0(_DAT_1899dbad0,1,0x48);
        if (puVar5 != (undefined8 *)0x0) {
          *puVar5 = 0;
          puVar5[1] = 0;
          puVar5[2] = 0;
          puVar5[3] = 0;
          puVar5[4] = 0;
          puVar5[5] = 0;
          puVar5[6] = 0;
          puVar5[7] = 0;
          puVar5[8] = 0;
        }
        func_0x0001803f72c0(0x1899db6b0);
        puVar5[1] = param_1;
        puVar5[2] = 0;
        *(undefined1 *)((longlong)puVar5 + 0x32) = *(undefined1 *)(lVar6 + 0x32);
        *(undefined2 *)(puVar5 + 6) = 0xffff;
        *(undefined1 *)((longlong)puVar5 + 0x33) = 1;
        FUN_1804fd200(param_1,puVar5);
      }
      FUN_18042e2c0(uVar4,uVar4,lVar1,puVar5);
      return uVar4;
    }
    puVar5 = (undefined8 *)
             FUN_1804f17f0(auStack_40,&UNK_1881a2808,*(undefined8 *)(param_2 + 0x20),
                           *(undefined8 *)(param_2 + 0xa8));
    if (0xf < (ulonglong)puVar5[3]) {
      puVar5 = (undefined8 *)*puVar5;
    }
    uVar4 = FUN_1804303f0(_DAT_1899db1c0,&UNK_188195170,&UNK_1881a2198,puVar5);
    FUN_180447cf0(uVar4,0);
    uStackX_18 = uVar4;
    FUN_1804ff8e0(&uStackX_18,&UNK_188d08588);
  }
  uVar4 = FUN_1804318e0(&UNK_188195548,&UNK_1881a27c8);
  FUN_180447cf0(uVar4,0);
  uStackX_18 = uVar4;
  FUN_1804ff8e0(&uStackX_18,&UNK_188d08588);
  pcVar2 = (code *)swi(3);
  uVar4 = (*pcVar2)();
  return uVar4;
}



/* ================= 0x18044d640 ================= */
/* name   = FUN_18044d640 */
/* entry  = 18044d640 */
/* body   = 88 bytes */
/* sig    = undefined FUN_18044d640() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_18044d640(void)

{
  undefined4 uVar1;
  longlong lVar2;
  longlong lVar3;
  
  uVar1 = GetLastError();
  lVar3 = (longlong)_DAT_18993b6c0;
  lVar2 = TlsGetValue(*_DAT_1899db5e0);
  if (lVar2 == 0) {
    GetLastError();
  }
  **(undefined4 **)(*(longlong *)(*(longlong *)(lVar2 + 0x10) + 0x60) + lVar3 * 8) = uVar1;
  return;
}



/* ================= 0x180444260 ================= */
/* name   = FUN_180444260 */
/* entry  = 180444260 */
/* body   = 196 bytes */
/* sig    = undefined FUN_180444260() */


char * FUN_180444260(longlong param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  char cVar1;
  code *pcVar2;
  char *pcVar3;
  char *pcVar4;
  char ****ppppcVar5;
  char ***apppcStack_30 [2];
  longlong lStack_20;
  ulonglong uStack_18;
  
  if (param_1 == 0) {
    pcVar3 = (char *)0x0;
  }
  else {
    FUN_1804f3320(apppcStack_30,param_1 + 0x14,param_3,param_4,0xfffffffffffffffe);
    pcVar3 = (char *)CoTaskMemAlloc(lStack_20 + 1);
    ppppcVar5 = apppcStack_30;
    pcVar4 = pcVar3;
    if (0xf < uStack_18) {
      ppppcVar5 = (char ****)apppcStack_30[0];
    }
    do {
      cVar1 = *(char *)ppppcVar5;
      *pcVar4 = cVar1;
      ppppcVar5 = (char ****)((longlong)ppppcVar5 + 1);
      pcVar4 = pcVar4 + 1;
    } while (cVar1 != '\0');
    if (0xf < uStack_18) {
      ppppcVar5 = (char ****)apppcStack_30[0];
      if (0xfff < uStack_18 + 1) {
        if (((ulonglong)apppcStack_30[0] & 0x1f) != 0) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          pcVar4 = (char *)(*pcVar2)();
          return pcVar4;
        }
        ppppcVar5 = (char ****)apppcStack_30[0][-1];
        if (apppcStack_30[0] <= ppppcVar5) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          pcVar4 = (char *)(*pcVar2)();
          return pcVar4;
        }
        if ((ulonglong)((longlong)apppcStack_30[0] - (longlong)ppppcVar5) < 8) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          pcVar4 = (char *)(*pcVar2)();
          return pcVar4;
        }
        if (0x27 < (ulonglong)((longlong)apppcStack_30[0] - (longlong)ppppcVar5)) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          pcVar4 = (char *)(*pcVar2)();
          return pcVar4;
        }
      }
      thunk_FUN_18050a3b8(ppppcVar5);
    }
  }
  return pcVar3;
}



/* ================= 0x1804450f0 ================= */
/* name   = FUN_1804450f0 */
/* entry  = 1804450f0 */
/* body   = 463 bytes */
/* sig    = undefined FUN_1804450f0() */


longlong FUN_1804450f0(longlong param_1)

{
  code *pcVar1;
  ulonglong uVar2;
  longlong lVar3;
  longlong lVar4;
  longlong lVar5;
  longlong lVar6;
  ulonglong uVar7;
  byte *pbVar8;
  int iVar9;
  longlong *plVar10;
  int iVar11;
  longlong lStackX_8;
  longlong lStack_80;
  longlong lStack_78;
  longlong lStack_70;
  longlong lStack_68;
  undefined8 uStack_60;
  longlong lStack_58;
  byte bStack_50;
  undefined7 uStack_4f;
  undefined8 uStack_40;
  ulonglong uStack_38;
  
  lVar6 = 0;
  if (param_1 != 0) {
    lStack_80 = 0;
    lStack_78 = 0;
    lStack_70 = 0;
    lStack_68 = 0;
    uStack_60 = 0;
    lStack_58 = 0;
    lVar6 = FUN_180444800(0,&lStackX_8,&lStack_80,&lStack_68,0xfffffffffffffffe);
    lVar3 = lStack_68;
    lVar5 = lStack_78;
    lVar4 = lStack_80;
    if (lStackX_8 != 0) {
      iVar11 = 0;
      iVar9 = (int)(lStack_78 - lStack_80 >> 5) + -1;
      if (-1 < iVar9) {
        plVar10 = (longlong *)(lStack_68 + (longlong)iVar9 * 8);
        do {
          uStack_38 = 0xf;
          uStack_40 = 0;
          bStack_50 = 0;
          FUN_1803f91b0(&bStack_50,(longlong)iVar9 * 0x20 + lVar4,0,0xffffffffffffffff);
          pbVar8 = &bStack_50;
          if (0xf < uStack_38) {
            pbVar8 = (byte *)CONCAT71(uStack_4f,bStack_50);
          }
          FUN_180500230((longlong)iVar11 + *(int *)(*plVar10 + 0x24) + lVar6,pbVar8);
          iVar11 = iVar11 + ((int)uStack_40 - *(int *)(*plVar10 + 0x20));
          if (0xf < uStack_38) {
            uVar2 = CONCAT71(uStack_4f,bStack_50);
            uVar7 = uVar2;
            if (0xfff < uStack_38 + 1) {
              if ((bStack_50 & 0x1f) != 0) {
                FUN_180509dc8();
                break;
              }
              uVar7 = *(ulonglong *)(uVar2 - 8);
              if (uVar2 <= uVar7) {
                FUN_180509dc8();
                pcVar1 = (code *)swi(3);
                lVar6 = (*pcVar1)();
                return lVar6;
              }
              if (uVar2 - uVar7 < 8) {
                FUN_180509dc8();
                pcVar1 = (code *)swi(3);
                lVar6 = (*pcVar1)();
                return lVar6;
              }
              if (0x27 < uVar2 - uVar7) {
                FUN_180509dc8();
                pcVar1 = (code *)swi(3);
                lVar6 = (*pcVar1)();
                return lVar6;
              }
            }
            thunk_FUN_18050a3b8(uVar7);
          }
          plVar10 = plVar10 + -1;
          iVar9 = iVar9 + -1;
        } while (-1 < iVar9);
      }
    }
    if (lVar3 != 0) {
      FUN_180452930(&lStack_68,lVar3,lStack_58 - lVar3 >> 3);
    }
    lVar3 = lVar4;
    if (lVar4 != 0) {
      for (; lVar3 != lVar5; lVar3 = lVar3 + 0x20) {
        FUN_1803ed580(lVar3);
      }
      FUN_1804f3960(&lStack_80,lVar4,lStack_70 - lVar4 >> 5);
    }
  }
  return lVar6;
}



/* ================= 0x1804452c0 ================= */
/* name   = FUN_1804452c0 */
/* entry  = 1804452c0 */
/* body   = 261 bytes */
/* sig    = undefined FUN_1804452c0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1804452c0(longlong param_1,longlong param_2)

{
  int iVar1;
  undefined8 uVar2;
  ulonglong uVar3;
  undefined8 ***pppuVar4;
  uint uVar5;
  ulonglong uVar6;
  undefined8 uVar7;
  undefined8 **appuStack_30 [2];
  int iStack_20;
  ulonglong uStack_18;
  
  if ((param_1 != 0) && (uVar7 = 0xfffffffffffffffe, param_2 != 0)) {
    FUN_1804f3400(appuStack_30);
    iVar1 = iStack_20;
    uVar2 = FUN_1804eb6e0(_DAT_1899db240,1);
    uVar2 = FUN_180445cf0(uVar2,(longlong)(iVar1 + 1));
    func_0x0001803edc70(param_1,param_1 + 0x10,uVar2);
    uVar3 = 0;
    uVar6 = uVar3;
    if (0 < iStack_20) {
      do {
        pppuVar4 = appuStack_30;
        if (7 < uStack_18) {
          pppuVar4 = (undefined8 ***)appuStack_30[0];
        }
        *(undefined2 *)(*(longlong *)(param_1 + 0x10) + 0x20 + uVar3) =
             *(undefined2 *)(uVar3 + (longlong)pppuVar4);
        uVar5 = (int)uVar6 + 1;
        uVar3 = uVar3 + 2;
        uVar6 = (ulonglong)uVar5;
      } while ((int)uVar5 < iStack_20);
    }
    *(undefined2 *)(*(longlong *)(param_1 + 0x10) + 0x20 + (longlong)iStack_20 * 2) = 0;
    *(int *)(param_1 + 0x20) = iStack_20;
    *(undefined4 *)(param_1 + 0x24) = 0;
    func_0x0001803edc70(param_1,param_1 + 0x18,0,0,uVar7);
    if (7 < uStack_18) {
      FUN_1803f9830(appuStack_30,appuStack_30[0],uStack_18 + 1);
    }
  }
  return;
}



/* ================= 0x180444330 ================= */
/* name   = FUN_180444330 */
/* entry  = 180444330 */
/* body   = 186 bytes */
/* sig    = undefined FUN_180444330() */


void FUN_180444330(longlong param_1,char *param_2,int param_3,undefined8 param_4)

{
  char cVar1;
  code *pcVar2;
  char ****ppppcVar3;
  char ***apppcStack_30 [3];
  ulonglong uStack_18;
  
  if (param_1 == 0) {
    *param_2 = '\0';
  }
  else {
    FUN_1804f3350(apppcStack_30,param_1 + 0x14,param_3 + -1,param_4,0xfffffffffffffffe);
    ppppcVar3 = apppcStack_30;
    if (0xf < uStack_18) {
      ppppcVar3 = (char ****)apppcStack_30[0];
    }
    do {
      cVar1 = *(char *)ppppcVar3;
      *param_2 = cVar1;
      param_2 = param_2 + 1;
      ppppcVar3 = (char ****)((longlong)ppppcVar3 + 1);
    } while (cVar1 != '\0');
    if (0xf < uStack_18) {
      ppppcVar3 = (char ****)apppcStack_30[0];
      if (0xfff < uStack_18 + 1) {
        if (((ulonglong)apppcStack_30[0] & 0x1f) != 0) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
        ppppcVar3 = (char ****)apppcStack_30[0][-1];
        if (apppcStack_30[0] <= ppppcVar3) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
        if ((ulonglong)((longlong)apppcStack_30[0] - (longlong)ppppcVar3) < 8) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
        if (0x27 < (ulonglong)((longlong)apppcStack_30[0] - (longlong)ppppcVar3)) {
          FUN_180509dc8();
          pcVar2 = (code *)swi(3);
          (*pcVar2)();
          return;
        }
      }
      thunk_FUN_18050a3b8(ppppcVar3);
    }
  }
  return;
}



/* ================= 0x1804443f0 ================= */
/* name   = FUN_1804443f0 */
/* entry  = 1804443f0 */
/* body   = 101 bytes */
/* sig    = undefined FUN_1804443f0() */


undefined2 * FUN_1804443f0(longlong param_1)

{
  int *piVar1;
  int iVar2;
  undefined2 *puVar3;
  undefined2 *puVar4;
  
  if (param_1 == 0) {
    return (undefined2 *)0x0;
  }
  iVar2 = func_0x0001802bbf30();
  puVar3 = (undefined2 *)CoTaskMemAlloc((longlong)(iVar2 + 1) * 2);
  piVar1 = (int *)(param_1 + 0x10);
  iVar2 = 0;
  if (0 < *piVar1) {
    puVar4 = puVar3;
    do {
      iVar2 = iVar2 + 1;
      *puVar4 = *(undefined2 *)((param_1 - (longlong)puVar3) + 0x14 + (longlong)puVar4);
      puVar4 = puVar4 + 1;
    } while (iVar2 < *piVar1);
  }
  puVar3[*piVar1] = 0;
  return puVar3;
}



/* ================= 0x1804453d0 ================= */
/* name   = FUN_1804453d0 */
/* entry  = 1804453d0 */
/* body   = 161 bytes */
/* sig    = undefined FUN_1804453d0() */


longlong FUN_1804453d0(longlong param_1)

{
  longlong *plVar1;
  longlong lVar2;
  longlong lVar3;
  longlong lVar4;
  
  if (param_1 == 0) {
    return 0;
  }
  lVar4 = 0;
  lVar2 = param_1;
  do {
    plVar1 = (longlong *)(lVar2 + 0x10);
    lVar2 = *(longlong *)(lVar2 + 0x18);
    lVar4 = lVar4 + *(longlong *)(*plVar1 + 0x18);
  } while (lVar2 != 0);
  lVar3 = CoTaskMemAlloc(lVar4 * 2 + 2);
  lVar2 = lVar4;
  while (lVar2 != 0) {
    FUN_180500230(lVar3 + (longlong)*(int *)(param_1 + 0x24) * 2,
                  *(longlong *)(param_1 + 0x10) + 0x20,
                  (longlong)*(int *)(*(longlong *)(param_1 + 0x10) + 0x18) * 2);
    param_1 = *(longlong *)(param_1 + 0x18);
    lVar2 = param_1;
  }
  *(undefined2 *)(lVar3 + lVar4 * 2) = 0;
  return lVar3;
}



/* ================= 0x180445480 ================= */
/* name   = FUN_180445480 */
/* entry  = 180445480 */
/* body   = 225 bytes */
/* sig    = undefined FUN_180445480() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_180445480(longlong param_1,short *param_2)

{
  short sVar1;
  short *psVar2;
  undefined8 uVar3;
  longlong lVar4;
  int iVar5;
  longlong lVar6;
  
  if ((param_1 != 0) && (param_2 != (short *)0x0)) {
    iVar5 = 0;
    sVar1 = *param_2;
    psVar2 = param_2;
    while (sVar1 != 0) {
      psVar2 = psVar2 + 1;
      iVar5 = iVar5 + 1;
      sVar1 = *psVar2;
    }
    uVar3 = FUN_1804eb6e0(_DAT_1899db240,1);
    uVar3 = FUN_180445cf0(uVar3,(longlong)(iVar5 + 1));
    func_0x0001803edc70(param_1,param_1 + 0x10,uVar3);
    if (0 < iVar5) {
      lVar4 = 0x20;
      lVar6 = (longlong)iVar5;
      do {
        *(undefined2 *)(lVar4 + *(longlong *)(param_1 + 0x10)) =
             *(undefined2 *)((longlong)param_2 + lVar4 + -0x20);
        lVar6 = lVar6 + -1;
        lVar4 = lVar4 + 2;
      } while (lVar6 != 0);
    }
    *(undefined2 *)(*(longlong *)(param_1 + 0x10) + 0x20 + (longlong)iVar5 * 2) = 0;
    *(int *)(param_1 + 0x20) = iVar5;
    *(undefined4 *)(param_1 + 0x24) = 0;
    func_0x0001803edc70(param_1,param_1 + 0x18,0);
  }
  return;
}



/* ================= 0x180444460 ================= */
/* name   = FUN_180444460 */
/* entry  = 180444460 */
/* body   = 116 bytes */
/* sig    = undefined FUN_180444460() */


void FUN_180444460(longlong param_1,undefined2 *param_2,int param_3)

{
  int iVar1;
  undefined2 *puVar2;
  longlong lVar3;
  
  if (param_1 == 0) {
    *param_2 = 0;
    return;
  }
  iVar1 = func_0x0001802bbf30();
  if (param_3 + -1 < iVar1) {
    iVar1 = param_3 + -1;
  }
  if (0 < iVar1) {
    puVar2 = param_2;
    lVar3 = (longlong)iVar1;
    do {
      *puVar2 = *(undefined2 *)((param_1 - (longlong)param_2) + 0x14 + (longlong)puVar2);
      puVar2 = puVar2 + 1;
      lVar3 = lVar3 + -1;
    } while (lVar3 != 0);
  }
  param_2[iVar1] = 0;
  return;
}



/* ================= 0x1804444f0 ================= */
/* name   = FUN_1804444f0 */
/* entry  = 1804444f0 */
/* body   = 55 bytes */
/* sig    = undefined FUN_1804444f0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 * FUN_1804444f0(short *param_1)

{
  short *psVar1;
  short sVar2;
  code *pcVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  uint uVar6;
  
  if (param_1 == (short *)0x0) {
    return (undefined8 *)0x0;
  }
  uVar6 = 0;
  sVar2 = *param_1;
  psVar1 = param_1;
  while (sVar2 != 0) {
    psVar1 = psVar1 + 1;
    uVar6 = uVar6 + 1;
    sVar2 = *psVar1;
  }
  puVar4 = _DAT_1899dbb50;
  if (uVar6 != 0) {
    if ((longlong)(int)(uVar6 * 2 + 2) + 0x18U < (ulonglong)uVar6) {
      FUN_1804489d0();
      pcVar3 = (code *)swi(3);
      puVar4 = (undefined8 *)(*pcVar3)();
      return puVar4;
    }
    puVar4 = (undefined8 *)func_0x0001804df180();
    *puVar4 = _DAT_1899db248;
    puVar4[1] = 0;
    *(uint *)(puVar4 + 2) = uVar6;
    *(undefined2 *)((longlong)puVar4 + (longlong)(int)uVar6 * 2 + 0x14) = 0;
  }
  uVar5 = func_0x0001804f1130(puVar4);
  FUN_180500230(uVar5,param_1,(longlong)(int)(uVar6 * 2));
  return puVar4;
}



/* ================= 0x180432d70 ================= */
/* name   = FUN_180432d70 */
/* entry  = 180432d70 */
/* body   = 4 bytes */
/* sig    = undefined FUN_180432d70() */


undefined8 FUN_180432d70(undefined8 *param_1)

{
  return *param_1;
}



/* ================= 0x1804fb160 ================= */
/* name   = FUN_1804fb160 */
/* entry  = 1804fb160 */
/* body   = 388 bytes */
/* sig    = undefined FUN_1804fb160() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong * FUN_1804fb160(longlong *param_1,undefined8 param_2)

{
  code *pcVar1;
  int iVar2;
  longlong *plVar3;
  undefined8 *puVar4;
  longlong *plStackX_8;
  longlong *plStackX_18;
  undefined8 uStackX_20;
  longlong *plStack_50;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined8 uStack_38;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  
  if (param_1 == (longlong *)0x0) {
    plStackX_18 = (longlong *)0x0;
  }
  else {
    plStackX_8 = param_1;
    if (*(char *)(*param_1 + 0x141) == '\0') {
      uStackX_20 = 0x189be14d8;
      func_0x0001803f4990(0x189be14d8);
      FUN_1804f9aa0(0x189be14f0,&plStack_50,&plStackX_8,param_1);
      if ((((longlong)plStack_50 - _DAT_189be1500 & 0xffffffffffffffe0U) + _DAT_189be1500 ==
           _DAT_189be1508) && (CONCAT44(uStack_44,uStack_48) == 0)) {
        puVar4 = (undefined8 *)FUN_18042e650(param_1);
        if ((*param_1 != _DAT_1899db488) || (_DAT_1899db478 == 0)) {
          uStack_38 = puVar4;
          FUN_1804e3f40(param_1,FUN_1804facd0,0,&plStackX_8,&plStack_50);
          uStack_30 = CONCAT31(uStack_30._1_3_,plStackX_8 != (longlong *)0x0);
          uStack_48 = (undefined4)uStack_38;
          uStack_44 = uStack_38._4_4_;
          uStack_40 = uStack_30;
          uStack_3c = uStack_2c;
          plStack_50 = param_1;
          FUN_1804fa070(0x189be14f0,&uStack_38,&plStack_50,&plStack_50);
        }
      }
      else {
        puVar4 = *(undefined8 **)(CONCAT44(uStack_44,uStack_48) + 8);
      }
      iVar2 = (**(code **)*puVar4)(puVar4,param_2,&plStackX_18);
      if (iVar2 < 0) {
        FUN_1804482f0(iVar2,1);
        pcVar1 = (code *)swi(3);
        plVar3 = (longlong *)(*pcVar1)();
        return plVar3;
      }
      func_0x0001803f72c0(0x189be14d8);
    }
    else {
      plVar3 = (longlong *)FUN_1804f9870();
      (**(code **)(*plVar3 + 8))(plVar3);
      plStackX_18 = plVar3;
    }
  }
  return plStackX_18;
}



/* ================= 0x1804173c0 ================= */
/* name   = FUN_1804173c0 */
/* entry  = 1804173c0 */
/* body   = 828 bytes */
/* sig    = undefined FUN_1804173c0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_1804173c0(undefined8 *param_1,longlong param_2)

{
  longlong *plVar1;
  int *piVar2;
  code *pcVar3;
  byte bVar4;
  int iVar5;
  longlong lVar6;
  undefined8 uVar7;
  ulonglong uVar8;
  longlong lVar9;
  ulonglong uVar10;
  ulonglong uVar11;
  longlong *plVar12;
  ulonglong uVar13;
  longlong *plVar14;
  longlong *plVar15;
  longlong *plStackX_18;
  longlong *plStackX_20;
  longlong *plStack_108;
  undefined8 uStack_100;
  longlong *plStack_f8;
  undefined8 uStack_e8;
  undefined8 uStack_e0;
  undefined1 auStack_d8 [8];
  undefined4 uStack_d0;
  undefined8 uStack_c8;
  longlong *plStack_c0;
  undefined8 uStack_b8;
  longlong lStack_b0;
  longlong *plStack_a8;
  longlong lStack_a0;
  longlong lStack_98;
  longlong *plStack_90;
  longlong *plStack_88;
  longlong *plStack_80;
  longlong *plStack_78;
  undefined8 uStack_70;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined1 auStack_58 [32];
  
  uStack_c8 = 0xfffffffffffffffe;
  iVar5 = (**(code **)*param_1)(param_1,&DAT_18819c300,&plStackX_20);
  if (-1 < iVar5) {
    lVar6 = (**(code **)(*plStackX_20 + 0x18))();
    (**(code **)(*plStackX_20 + 0x10))();
    return lVar6;
  }
  iVar5 = (**(code **)*param_1)(param_1,&DAT_18819c370,&plStackX_18);
  plVar15 = plStackX_18;
  if (iVar5 < 0) {
    uVar7 = FUN_1804310d0(iVar5,1);
    FUN_180447cf0(uVar7,0);
    uStack_100 = uVar7;
    FUN_1804ff8e0(&uStack_100,&UNK_188d08588);
    pcVar3 = (code *)swi(3);
    lVar6 = (*pcVar3)();
    return lVar6;
  }
  plStack_c0 = plStackX_18;
  uStack_b8 = 0x1899dba30;
  func_0x0001803f4990(0x1899dba30);
  uVar11 = _DAT_1899db9b8 & (ulonglong)plVar15;
  uVar13 = 0;
  uVar10 = _DAT_1899db9b8;
  do {
    lVar6 = (uVar11 >> 6) * 0x20;
    plVar14 = (longlong *)(_DAT_1899db9d8 + lVar6);
    uVar8 = 1L << ((byte)uVar11 & 0x3f);
    if ((plVar14[1] & uVar8) == 0) {
      if (((plVar14[2] & uVar8) == 0) || (_DAT_1899db9e0 <= uVar13)) break;
    }
    else {
      bVar4 = FUN_180415ac0(plVar14[1] & uVar8 - 1);
      plVar12 = (longlong *)((ulonglong)bVar4 * 0x10 + *plVar14);
      uVar10 = _DAT_1899db9b8;
      if (plVar15 == (longlong *)*plVar12) {
        lStack_b0 = _DAT_1899db9c0;
        plVar14 = (longlong *)(lVar6 + _DAT_1899db9c0);
        goto LAB_180417541;
      }
    }
    uVar13 = uVar13 + 1;
    uVar11 = uVar11 + uVar13 & uVar10;
  } while( true );
  plStack_a8 = _DAT_1899db9c8;
  plVar12 = (longlong *)0x0;
  plVar14 = _DAT_1899db9c8;
LAB_180417541:
  lStack_a0 = _DAT_1899db9c0;
  lStack_98 = _DAT_1899db9c0;
  plVar14 = (longlong *)
            (((longlong)plVar14 - _DAT_1899db9c0 & 0xffffffffffffffe0U) + _DAT_1899db9c0);
  plStack_90 = _DAT_1899db9c8;
  plStack_78 = _DAT_1899db9c8;
  uStack_70 = 0;
  uStack_e8 = plVar14;
  uStack_e0 = plVar12;
  if ((plVar14 != _DAT_1899db9c8) || (plVar12 != (longlong *)0x0)) {
    lVar6 = FUN_1804fb2f0((int)plVar12[1]);
    if (lVar6 != 0) {
      LOCK();
      piVar2 = (int *)(lVar6 + 0xac);
      iVar5 = *piVar2;
      *piVar2 = *piVar2 + 1;
      UNLOCK();
      plVar14 = uStack_e8;
      plVar15 = plStackX_18;
      if (1 < iVar5 + 1) {
        (**(code **)(*plStackX_18 + 0x10))();
        goto LAB_1804176d1;
      }
    }
    uStack_68 = (undefined4)uStack_e8;
    uStack_64 = uStack_e8._4_4_;
    uStack_60 = (undefined4)uStack_e0;
    uStack_5c = uStack_e0._4_4_;
    lVar6 = func_0x000180452b10(plVar14,0x1899db9b0,plVar12);
    _DAT_1899db9e8 = _DAT_1899db9e8 + -1;
    _DAT_1899db9f0 = _DAT_1899db9f0 + 1;
    if (lVar6 == (ulonglong)*(byte *)(plVar14 + 3) * 0x10 + *plVar14) {
      plStack_88 = _DAT_1899db9c8;
      do {
        plVar12 = plVar14 + 4;
        if (plVar12 == _DAT_1899db9c8) break;
        plVar1 = plVar14 + 7;
        plVar14 = plVar12;
      } while ((char)*plVar1 == '\0');
      plStack_80 = _DAT_1899db9c8;
      if (plVar12 == _DAT_1899db9c8) {
        plStack_f8 = _DAT_1899db9c8;
      }
    }
  }
  iVar5 = (**(code **)*param_1)(param_1,&DAT_18819c310,&plStack_108);
  lVar9 = param_2;
  if (-1 < iVar5) {
    lVar9 = FUN_180432e10(plStack_108,param_2);
    (**(code **)(*plStack_108 + 0x10))();
  }
  lVar6 = FUN_180448bf0(param_1,lVar9);
  if (lVar6 == 0) {
    if (((*(char *)(lVar9 + 0x6a) != '\x12') || ((*(byte *)(lVar9 + 0x10c) & 0x20) != 0)) ||
       (*(char *)(lVar9 + 0x13e) != '\0')) {
      lVar9 = param_2;
    }
    lVar6 = FUN_1804457f0(lVar9);
    *(longlong **)(lVar6 + 0x10) = plVar15;
    *(undefined4 *)(lVar6 + 0xac) = 1;
    uStack_d0 = FUN_1804fb630(lVar6,0);
    FUN_18041f110(0x1899db9b0,auStack_58,auStack_d8,auStack_d8);
  }
LAB_1804176d1:
  func_0x0001803f72c0(0x1899dba30);
  return lVar6;
}



/* ================= 0x180444d70 ================= */
/* name   = FUN_180444d70 */
/* entry  = 180444d70 */
/* body   = 301 bytes */
/* sig    = undefined FUN_180444d70() */


longlong FUN_180444d70(undefined8 param_1,longlong param_2)

{
  code *pcVar1;
  int iVar2;
  undefined4 uVar3;
  longlong lVar4;
  undefined8 uVar5;
  undefined4 uStackX_10;
  undefined4 uStackX_14;
  undefined8 uStackX_18;
  undefined8 uStackX_20;
  
  if (param_2 == 0) {
    return 0;
  }
  uStackX_10 = *(undefined4 *)(param_2 + 0x18);
  uStackX_14 = 0;
  lVar4 = Ordinal_15(param_1,1,&uStackX_10);
  if (lVar4 == 0) {
    uVar5 = FUN_1804310d0(0x8007000e,1);
    FUN_180447cf0(uVar5,0);
    uStackX_18 = uVar5;
    FUN_1804ff8e0(&uStackX_18,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar4 = (*pcVar1)();
    return lVar4;
  }
  iVar2 = Ordinal_23(lVar4,&uStackX_20);
  if (iVar2 < 0) {
    Ordinal_16(lVar4);
    uVar5 = FUN_1804310d0(iVar2,1);
    FUN_180447cf0(uVar5,0);
    uStackX_18 = uVar5;
    FUN_1804ff8e0(&uStackX_18,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar4 = (*pcVar1)();
    return lVar4;
  }
  uVar3 = FUN_180432610(param_2);
  FUN_180500230(uStackX_20,param_2 + 0x20,uVar3);
  iVar2 = Ordinal_24(lVar4);
  if (-1 < iVar2) {
    return lVar4;
  }
  Ordinal_16(lVar4);
  uVar5 = FUN_1804310d0(iVar2,1);
  FUN_180447cf0(uVar5,0);
  uStackX_18 = uVar5;
  FUN_1804ff8e0(&uStackX_18,&UNK_188d08588);
  pcVar1 = (code *)swi(3);
  lVar4 = (*pcVar1)();
  return lVar4;
}



/* ================= 0x180444ea0 ================= */
/* name   = FUN_180444ea0 */
/* entry  = 180444ea0 */
/* body   = 589 bytes */
/* sig    = undefined FUN_180444ea0() */


longlong FUN_180444ea0(short param_1,undefined8 param_2,longlong param_3)

{
  code *pcVar1;
  int iVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  longlong lVar5;
  short asStackX_18 [4];
  int aiStackX_20 [2];
  int aiStack_28 [2];
  undefined8 uStack_20;
  undefined8 auStack_18 [2];
  
  if (param_3 == 0) {
    return 0;
  }
  iVar2 = Ordinal_77(param_3,asStackX_18);
  if (iVar2 < 0) {
    uVar4 = FUN_1804310d0(iVar2,1);
    FUN_180447cf0(uVar4,0);
    uStack_20 = uVar4;
    FUN_1804ff8e0(&uStack_20,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar5 = (*pcVar1)();
    return lVar5;
  }
  if (asStackX_18[0] != param_1) {
    uVar4 = FUN_1804310d0(0x80070057,1);
    FUN_180447cf0(uVar4,0);
    uStack_20 = uVar4;
    FUN_1804ff8e0(&uStack_20,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar5 = (*pcVar1)();
    return lVar5;
  }
  iVar2 = Ordinal_17(param_3);
  if (iVar2 != 1) {
    uVar4 = FUN_1804310d0(0x80070057,1);
    FUN_180447cf0(uVar4,0);
    uStack_20 = uVar4;
    FUN_1804ff8e0(&uStack_20,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar5 = (*pcVar1)();
    return lVar5;
  }
  iVar2 = Ordinal_20(param_3,1,aiStack_28);
  if (iVar2 < 0) {
    uVar4 = FUN_1804310d0(iVar2,1);
    FUN_180447cf0(uVar4,0);
    uStack_20 = uVar4;
    FUN_1804ff8e0(&uStack_20,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar5 = (*pcVar1)();
    return lVar5;
  }
  iVar2 = Ordinal_19(param_3,1,aiStackX_20);
  if (iVar2 < 0) {
    uVar4 = FUN_1804310d0(iVar2,1);
    FUN_180447cf0(uVar4,0);
    uStack_20 = uVar4;
    FUN_1804ff8e0(&uStack_20,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar5 = (*pcVar1)();
    return lVar5;
  }
  uVar4 = FUN_1804eb6e0(param_2,1);
  lVar5 = FUN_180445cf0(uVar4,(longlong)((aiStackX_20[0] - aiStack_28[0]) + 1));
  iVar2 = Ordinal_23(param_3,auStack_18);
  if (iVar2 < 0) {
    uVar4 = FUN_1804310d0(iVar2,1);
    FUN_180447cf0(uVar4,0);
    uStack_20 = uVar4;
    FUN_1804ff8e0(&uStack_20,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    lVar5 = (*pcVar1)();
    return lVar5;
  }
  uVar3 = FUN_180432610(lVar5);
  FUN_180500230(lVar5 + 0x20,auStack_18[0],uVar3);
  iVar2 = Ordinal_24(param_3);
  if (-1 < iVar2) {
    return lVar5;
  }
  uVar4 = FUN_1804310d0(iVar2,1);
  FUN_180447cf0(uVar4,0);
  uStack_20 = uVar4;
  FUN_1804ff8e0(&uStack_20,&UNK_188d08588);
  pcVar1 = (code *)swi(3);
  lVar5 = (*pcVar1)();
  return lVar5;
}



/* ================= 0x1804f9870 ================= */
/* name   = FUN_1804f9870 */
/* entry  = 1804f9870 */
/* body   = 131 bytes */
/* sig    = undefined FUN_1804f9870() */


longlong * FUN_1804f9870(longlong param_1,undefined8 param_2)

{
  code *pcVar1;
  char cVar2;
  int iVar3;
  longlong *plVar4;
  longlong *aplStackX_18 [2];
  
  aplStackX_18[0] = (longlong *)FUN_180448230();
  if (aplStackX_18[0] == (longlong *)0x0) {
    iVar3 = (**(code **)**(undefined8 **)(param_1 + 0x10))
                      (*(undefined8 **)(param_1 + 0x10),param_2,aplStackX_18);
    if (iVar3 < 0) {
      FUN_1804482f0(iVar3,1);
      pcVar1 = (code *)swi(3);
      plVar4 = (longlong *)(*pcVar1)();
      return plVar4;
    }
    cVar2 = FUN_18042d0e0(param_1,param_2,aplStackX_18[0]);
    if (cVar2 == '\0') {
      (**(code **)(*aplStackX_18[0] + 0x10))();
      plVar4 = (longlong *)FUN_180448230(param_1,param_2);
      return plVar4;
    }
  }
  return aplStackX_18[0];
}



/* ================= 0x180445770 ================= */
/* name   = FUN_180445770 */
/* entry  = 180445770 */
/* body   = 115 bytes */
/* sig    = undefined FUN_180445770() */


undefined8 FUN_180445770(longlong param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  ulonglong uVar1;
  undefined8 uVar2;
  undefined8 ***pppuVar3;
  undefined8 **appuStack_30 [2];
  undefined4 uStack_20;
  ulonglong uStack_18;
  
  uVar1 = 0xffffffffffffffff;
  do {
    uVar1 = uVar1 + 1;
  } while (*(char *)(param_1 + uVar1) != '\0');
  FUN_1804f3430(appuStack_30,param_1,uVar1 & 0xffffffff,param_4,0xfffffffffffffffe);
  pppuVar3 = appuStack_30;
  if (7 < uStack_18) {
    pppuVar3 = (undefined8 ***)appuStack_30[0];
  }
  uVar2 = FUN_180445e10(pppuVar3,uStack_20);
  if (7 < uStack_18) {
    FUN_1803f9830(appuStack_30,appuStack_30[0],uStack_18 + 1);
  }
  return uVar2;
}



/* ================= 0x1804fe3e0 ================= */
/* name   = FUN_1804fe3e0 */
/* entry  = 1804fe3e0 */
/* body   = 10 bytes */
/* sig    = undefined FUN_1804fe3e0() */


void FUN_1804fe3e0(void)

{
  code *pcVar1;
  
  FUN_18042c2e0();
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



/* ================= 0x1804fe2a0 ================= */
/* name   = FUN_1804fe2a0 */
/* entry  = 1804fe2a0 */
/* body   = 5 bytes */
/* sig    = undefined FUN_1804fe2a0() */


void FUN_1804fe2a0(longlong param_1)

{
  if (param_1 == 0) {
    return;
  }
                    /* WARNING: Could not recover jumptable at 0x0001803f2020. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  CoTaskMemFree();
  return;
}



/* ================= 0x1804fe0e0 ================= */
/* name   = FUN_1804fe0e0 */
/* entry  = 1804fe0e0 */
/* body   = 5 bytes */
/* sig    = undefined FUN_1804fe0e0() */


longlong FUN_1804fe0e0(longlong param_1)

{
  return param_1 + 0x10;
}



/* ================= 0x1804fe070 ================= */
/* name   = FUN_1804fe070 */
/* entry  = 1804fe070 */
/* body   = 67 bytes */
/* sig    = undefined FUN_1804fe070() */


void FUN_1804fe070(longlong *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  code *pcVar1;
  undefined8 uVar2;
  undefined8 ***pppuVar3;
  undefined8 **appuStack_30 [3];
  ulonglong uStack_18;
  
  FUN_1804f0fb0(appuStack_30,*(undefined8 *)(*param_1 + 0x30),param_2,param_4,0xfffffffffffffffe);
  pppuVar3 = appuStack_30;
  if (0xf < uStack_18) {
    pppuVar3 = (undefined8 ***)appuStack_30[0];
  }
  uVar2 = func_0x000180436920(pppuVar3);
  FUN_180448320(uVar2,0);
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



/* ================= 0x1804fe050 ================= */
/* name   = FUN_1804fe050 */
/* entry  = 1804fe050 */
/* body   = 19 bytes */
/* sig    = undefined FUN_1804fe050() */


bool FUN_1804fe050(void)

{
  char cVar1;
  
  cVar1 = func_0x0001804423e0();
  return cVar1 == '\0';
}



/* ================= 0x1804fe100 ================= */
/* name   = FUN_1804fe100 */
/* entry  = 1804fe100 */
/* body   = 39 bytes */
/* sig    = undefined FUN_1804fe100() */


void FUN_1804fe100(undefined8 param_1,undefined8 param_2,longlong *param_3)

{
  char cVar1;
  
  cVar1 = FUN_18042d0e0();
  if (cVar1 != '\0') {
                    /* WARNING: Could not recover jumptable at 0x0001804fe11d. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(*param_3 + 8))(param_3);
    return;
  }
  return;
}



/* ================= 0x1804fe130 ================= */
/* name   = FUN_1804fe130 */
/* entry  = 1804fe130 */
/* body   = 28 bytes */
/* sig    = undefined FUN_1804fe130() */


void FUN_1804fe130(void)

{
  code *pcVar1;
  int iVar2;
  
  iVar2 = Ordinal_16();
  if (-1 < iVar2) {
    return;
  }
  FUN_1804482f0(iVar2,1);
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



