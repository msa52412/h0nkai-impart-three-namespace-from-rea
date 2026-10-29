// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x18043B3D3 ================= */
/* name   = FUN_18043b3c0 */
/* entry  = 18043b3c0 */
/* body   = 149 bytes */
/* sig    = undefined FUN_18043b3c0() */


longlong FUN_18043b3c0(int param_1)

{
  longlong lVar1;
  longlong lVar2;
  
  if (param_1 == -1) {
    return 0;
  }
  lVar1 = (longlong)param_1 * 8;
  lVar2 = *(longlong *)(lVar1 + DAT_1899dbbe8);
  if (lVar2 == 0) {
    lVar2 = FUN_180430150(*(undefined8 *)(PTR_PTR_1881a3628 + lVar1));
    if (lVar2 != 0) {
      if (*(char *)(lVar2 + 0x136) == '\0') {
        FUN_18043e4c0(lVar2);
      }
      *(longlong *)(lVar1 + DAT_1899dbbe8) = lVar2;
      return lVar2;
    }
    lVar2 = *(longlong *)(lVar1 + DAT_1899dbbe8);
  }
  return lVar2;
}



/* ================= 0x18044BC60 ================= */
/* name   = FUN_18044bc60 */
/* entry  = 18044bc60 */
/* body   = 584 bytes */
/* sig    = undefined FUN_18044bc60() */


void FUN_18044bc60(longlong param_1)

{
  int iVar1;
  longlong lVar2;
  longlong lVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  int iVar6;
  undefined8 *puVar7;
  ushort uVar8;
  ulonglong uVar9;
  
  if (*(undefined4 **)(param_1 + 0xc0) == (undefined4 *)0x0) {
    if (*(char *)(param_1 + 0x131) == '\0') {
      if ((*(ushort *)(param_1 + 300) != 0) && (*(longlong *)(param_1 + 0x38) == 0)) {
        uVar9 = (ulonglong)*(ushort *)(param_1 + 300);
        puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar9,8);
        puVar7 = puVar4;
        for (; uVar9 != 0; uVar9 = uVar9 - 1) {
          if (puVar7 != (undefined8 *)0x0) {
            *puVar7 = 0;
          }
          puVar7 = puVar7 + 1;
        }
        *(undefined8 **)(param_1 + 0x38) = puVar4;
        uVar8 = 0;
        if (*(short *)(param_1 + 300) != 0) {
          do {
            iVar6 = ((*(uint *)(*(longlong *)(param_1 + 0xd0) + 0x38) ^ 0x58833d25) + (uint)uVar8) -
                    *(int *)(param_1 + 200);
            iVar1 = *(int *)((DAT_188198e34 + -0x75cbfdcc) + DAT_1899dbaf8 + (longlong)iVar6 * 4);
            uVar5 = 0;
            if (iVar1 != -1) {
              uVar5 = *(undefined8 *)(PTR_PTR_1881a3628 + (longlong)iVar1 * 8);
            }
            uVar5 = FUN_180430150(uVar5,CONCAT71((int7)(int3)((uint)iVar6 >> 8),1));
            uVar9 = (ulonglong)uVar8;
            uVar8 = uVar8 + 1;
            *(undefined8 *)(*(longlong *)(param_1 + 0x38) + uVar9 * 8) = uVar5;
          } while (uVar8 < *(ushort *)(param_1 + 300));
        }
      }
    }
    else if (*(longlong *)(param_1 + 0x38) == 0) {
      FUN_1804ed600();
    }
  }
  else {
    lVar3 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
    lVar2 = *(longlong *)(param_1 + 0xc0);
    if ((*(ushort *)(lVar3 + 300) != 0) && (*(longlong *)(param_1 + 0x38) == 0)) {
      uVar9 = (ulonglong)*(ushort *)(lVar3 + 300);
      puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar9,8);
      puVar7 = puVar4;
      for (; uVar9 != 0; uVar9 = uVar9 - 1) {
        if (puVar7 != (undefined8 *)0x0) {
          *puVar7 = 0;
        }
        puVar7 = puVar7 + 1;
      }
      *(undefined8 **)(param_1 + 0x38) = puVar4;
      uVar8 = 0;
      if (*(short *)(lVar3 + 300) != 0) {
        do {
          iVar1 = *(int *)((DAT_188198e34 + -0x75cbfdcc) + DAT_1899dbaf8 +
                          (longlong)
                          (int)(((*(uint *)(*(longlong *)(lVar3 + 0xd0) + 0x38) ^ 0x58833d25) -
                                *(int *)(lVar3 + 200)) + (uint)uVar8) * 4);
          uVar5 = 0;
          if (iVar1 != -1) {
            uVar5 = *(undefined8 *)(PTR_PTR_1881a3628 + (longlong)iVar1 * 8);
          }
          uVar5 = FUN_1804ecb50(uVar5,lVar2 + 8,0);
          uVar5 = FUN_180430150(uVar5,1);
          uVar9 = (ulonglong)uVar8;
          uVar8 = uVar8 + 1;
          *(undefined8 *)(*(longlong *)(param_1 + 0x38) + uVar9 * 8) = uVar5;
        } while (uVar8 < *(ushort *)(lVar3 + 300));
      }
    }
  }
  return;
}



/* ================= 0x180430150 ================= */
/* name   = FUN_180430150 */
/* entry  = 180430150 */
/* body   = 527 bytes */
/* sig    = undefined FUN_180430150() */


undefined8 FUN_180430150(uint *param_1)

{
  uint uVar1;
  undefined8 uVar2;
  longlong local_18;
  longlong lStack_10;
  
  switch(*(undefined1 *)((longlong)param_1 + 10)) {
  case 1:
    return DAT_1899db1d8;
  case 2:
    return DAT_1899db1e0;
  case 3:
    return DAT_1899db240;
  case 4:
    return DAT_1899db1e8;
  case 5:
    return DAT_1899db1d0;
  case 6:
    return DAT_1899db1f0;
  case 7:
    return DAT_1899db1f8;
  case 8:
    return DAT_1899db200;
  case 9:
    return DAT_1899db208;
  case 10:
    return DAT_1899db220;
  case 0xb:
    return DAT_1899db228;
  case 0xc:
    return DAT_1899db230;
  case 0xd:
    return DAT_1899db238;
  case 0xe:
    return DAT_1899db248;
  case 0xf:
    uVar2 = FUN_180430150(*(undefined8 *)param_1,1);
    uVar2 = FUN_180439ef0(uVar2);
    return uVar2;
  default:
    return 0;
  case 0x11:
  case 0x12:
    uVar2 = FUN_18043b320(*param_1);
    return uVar2;
  case 0x13:
  case 0x1e:
    break;
  case 0x14:
    uVar2 = FUN_180430150(**(undefined8 **)param_1);
    uVar2 = FUN_1804eb6e0(uVar2,*(undefined1 *)(*(longlong *)param_1 + 8),1);
    return uVar2;
  case 0x15:
    uVar2 = FUN_180432a60(*(undefined8 *)param_1);
    return uVar2;
  case 0x16:
    return DAT_1899db320;
  case 0x18:
    return DAT_1899db210;
  case 0x19:
    return DAT_1899db218;
  case 0x1c:
    return DAT_1899db1c8;
  case 0x1d:
    uVar2 = FUN_180430150(*(undefined8 *)param_1);
    uVar2 = FUN_1804eb6e0(uVar2,1);
    return uVar2;
  }
  uVar1 = *param_1;
  if (uVar1 == 0xffffffff) {
    local_18 = 0;
    lStack_10 = 0;
  }
  else {
    local_18 = ((ulonglong)uVar1 * 0x34d04ba0e4db + 0xa13ee8c44cc682a ^ 0x43427e7d) + 0x10776301;
    lStack_10 = (ulonglong)uVar1 * 0x10 + (DAT_188198e40 + -0x77870e75) + DAT_1899dbaf8;
  }
  uVar2 = FUN_18042fe20(&local_18);
  return uVar2;
}



/* ================= 0x180437120 ================= */
/* name   = FUN_180437120 */
/* entry  = 180437120 */
/* body   = 279 bytes */
/* sig    = undefined FUN_180437120() */


undefined8 FUN_180437120(uint param_1)

{
  longlong lVar1;
  longlong lVar2;
  undefined8 uVar3;
  undefined *local_res10;
  
  lVar1 = (longlong)(int)param_1 * 8;
  if (*(longlong *)(DAT_1899dbbf8 + lVar1) == 0) {
    lVar2 = FUN_18043b320(*(int *)((ulonglong)param_1 * 0x20 +
                                  (DAT_188198e58 + -0x17a3b99) + DAT_1899dbaf8) + 0xe5af14b4U ^
                          (uint)((((ulonglong)param_1 * 0xb069 ^ 0x3e382f2d) * 0x24147491 >> 10 ^
                                 0x3e65ed2a) * 0x3857aaca >> 0xe));
    if ((*(short *)(lVar2 + 0x124) != 0) || (*(char *)(lVar2 + 0x131) != '\0')) {
      local_res10 = &DAT_1899db6b0;
      FUN_1803f4990();
      FUN_18044c400(lVar2,&local_res10);
      FUN_1803f72c0(local_res10);
    }
    uVar3 = *(undefined8 *)
             (*(longlong *)(lVar2 + 0x18) +
             (longlong)
             (int)(param_1 + 0x2822b502 +
                  (*(int *)(lVar2 + 200) - *(int *)(*(longlong *)(lVar2 + 0xd0) + 0x14))) * 8);
    *(undefined8 *)(DAT_1899dbbf8 + lVar1) = uVar3;
  }
  else {
    uVar3 = *(undefined8 *)(DAT_1899dbbf8 + lVar1);
  }
  return uVar3;
}



