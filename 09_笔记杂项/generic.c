// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 18044c84f ================= */
/* name   = FUN_18044c810 */
/* entry  = 18044c810 */
/* body   = 220 bytes */
/* sig    = undefined FUN_18044c810() */


void FUN_18044c810(longlong param_1)

{
  undefined8 *puVar1;
  undefined8 uVar2;
  undefined8 *puVar3;
  ushort uVar4;
  ulonglong uVar5;
  
  if (((*(longlong *)(param_1 + 0xc0) == 0) && (*(longlong *)(param_1 + 0x78) == 0)) &&
     (*(ushort *)(param_1 + 0x122) != 0)) {
    uVar5 = (ulonglong)*(ushort *)(param_1 + 0x122);
    puVar1 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar5,8);
    puVar3 = puVar1;
    for (; uVar5 != 0; uVar5 = uVar5 - 1) {
      if (puVar3 != (undefined8 *)0x0) {
        *puVar3 = 0;
      }
      puVar3 = puVar3 + 1;
    }
    uVar4 = 0;
    *(undefined8 **)(param_1 + 0x78) = puVar1;
    if (*(short *)(param_1 + 0x122) != 0) {
      do {
        uVar2 = FUN_18043b320(*(undefined4 *)
                               ((DAT_188198e94 + -0x72626879) + DAT_1899dbaf8 +
                               (longlong)
                               (int)((uint)uVar4 +
                                    ((*(uint *)(*(longlong *)(param_1 + 0xd0) + 0x20) ^ 0x21fe571d)
                                    - *(int *)(param_1 + 200))) * 4));
        uVar5 = (ulonglong)uVar4;
        uVar4 = uVar4 + 1;
        *(undefined8 *)(*(longlong *)(param_1 + 0x78) + uVar5 * 8) = uVar2;
      } while (uVar4 < *(ushort *)(param_1 + 0x122));
    }
  }
  return;
}



/* ================= 18042b910 ================= */
/* name   = FUN_18042b910 */
/* entry  = 18042b910 */
/* body   = 425 bytes */
/* sig    = undefined FUN_18042b910() */


void FUN_18042b910(longlong param_1,ushort *param_2)

{
  int iVar1;
  ulonglong uVar2;
  undefined8 uVar3;
  char *pcVar4;
  undefined8 uVar5;
  uint uVar6;
  longlong lVar8;
  ulonglong uVar9;
  byte local_40;
  undefined7 uStack_3f;
  undefined8 local_30;
  ulonglong local_28;
  ulonglong uVar7;
  
  lVar8 = *(longlong *)(param_2 + 4);
  uVar7 = 0;
  if ((*(ushort *)(lVar8 + 0x46) ^ 0x7883) != *param_2) {
    do {
      uVar3 = FUN_18043b320(*(undefined4 *)
                             ((DAT_188198e94 + -0x72626879) + DAT_1899dbaf8 +
                             (longlong)
                             (int)(((*(uint *)(lVar8 + 0x20) ^ 0x21fe571d) - *(int *)param_2) +
                                  (int)uVar7) * 4));
      iVar1 = *(int *)(*(longlong *)(param_2 + 4) + 0x30);
      uVar5 = *(undefined8 *)param_2;
      if ((*(uint *)(*(longlong *)(param_2 + 4) + 0x34) ^ 0x3399efb) - (int)uVar5 == -1) {
        return;
      }
      pcVar4 = (char *)FUN_18043ab50();
      local_28 = 0xf;
      local_30 = 0;
      local_40 = 0;
      uVar9 = 0;
      if (*pcVar4 != '\0') {
        uVar9 = 0xffffffffffffffff;
        do {
          uVar9 = uVar9 + 1;
        } while (pcVar4[uVar9] != '\0');
      }
      FUN_1803f92e0(&local_40,pcVar4,uVar9);
      uVar5 = FUN_18043ab50((iVar1 + -0x4b6accc7) - (int)uVar5);
      FUN_18042b6c0(*(undefined8 *)(param_1 + 8),uVar5,&local_40,uVar3);
      if (0xf < local_28) {
        uVar2 = CONCAT71(uStack_3f,local_40);
        uVar9 = uVar2;
        if (0xfff < local_28 + 1) {
          if ((local_40 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar9 = *(ulonglong *)(uVar2 - 8);
          if (uVar2 <= uVar9) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (uVar2 - uVar9 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < uVar2 - uVar9) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar9);
      }
      local_28 = 0xf;
      local_30 = 0;
      local_40 = 0;
      uVar6 = (int)uVar7 + 1;
      uVar7 = (ulonglong)uVar6;
      lVar8 = *(longlong *)(param_2 + 4);
    } while ((int)uVar6 < (int)(uint)(ushort)((*(ushort *)(lVar8 + 0x46) ^ 0x7883) - *param_2));
  }
  return;
}



/* ================= 180433db0 ================= */
/* name   = FUN_180433db0 */
/* entry  = 180433db0 */
/* body   = 100 bytes */
/* sig    = undefined FUN_180433db0() */


longlong FUN_180433db0(longlong param_1)

{
  uint uVar1;
  longlong lVar2;
  
  uVar1 = *(uint *)(*(longlong *)(param_1 + 0x10) + -0x5a6601071b4f6182);
  if (((uVar1 >> 0xf & 1) == 0) && ((uVar1 >> 8 & 1) == 0)) {
    return 0;
  }
  lVar2 = FUN_180434c40();
  if ((lVar2 != 0) && (*(int *)(lVar2 + 8) != -1)) {
    return (longlong)*(int *)(lVar2 + 8) + ((longlong)DAT_188198e8c ^ 0x227cd810U) + DAT_1899dbaf8;
  }
  return 0;
}



/* ================= 180434070 ================= */
/* name   = FUN_180434070 */
/* entry  = 180434070 */
/* body   = 117 bytes */
/* sig    = undefined FUN_180434070() */


void FUN_180434070(undefined8 param_1,undefined8 param_2)

{
  int *piVar1;
  longlong lVar2;
  longlong lVar3;
  
  lVar2 = 0;
  piVar1 = (int *)FUN_180434c40();
  lVar3 = lVar2;
  if (piVar1 != (int *)0x0) {
    if (*piVar1 != -1) {
      lVar3 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)*piVar1 * 8);
    }
    if (piVar1[2] != -1) {
      lVar2 = ((longlong)DAT_188198e8c ^ 0x227cd810U) + DAT_1899dbaf8 + (longlong)piVar1[2];
    }
  }
  FUN_1804fd490((int)*(char *)(lVar3 + 10),lVar2,param_2);
  return;
}



