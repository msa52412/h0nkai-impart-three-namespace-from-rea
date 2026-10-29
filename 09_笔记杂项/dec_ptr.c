// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x180434070 ================= */
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



/* ================= 0x1804340F0 ================= */
/* name   = FUN_1804340f0 */
/* entry  = 1804340f0 */
/* body   = 352 bytes */
/* sig    = undefined FUN_1804340f0() */


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

undefined8 FUN_1804340f0(undefined8 param_1,undefined8 *param_2,undefined1 *param_3)

{
  char cVar1;
  int iVar2;
  longlong lVar3;
  longlong lVar4;
  undefined8 uVar5;
  ulonglong uVar6;
  longlong lVar7;
  longlong lVar8;
  longlong lVar9;
  undefined8 local_res18;
  undefined8 auStack_40 [5];
  
  *param_3 = 0;
  auStack_40[0] = 0x18043411a;
  lVar3 = FUN_1804398b0();
  if (lVar3 != 0) {
    lVar9 = 0;
    if (*(int *)(lVar3 + 8) != -1) {
      lVar9 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)*(int *)(lVar3 + 8) * 8);
    }
    if (*(int *)(lVar3 + 4) == -1) {
      *param_3 = 1;
    }
    else {
      lVar3 = (longlong)*(int *)(lVar3 + 4) +
              ((longlong)DAT_188198e8c ^ 0x227cd810U) + DAT_1899dbaf8;
      if (lVar3 != 0) {
        auStack_40[0] = 0x180434189;
        lVar4 = FUN_180430150(*param_2,1);
        if (*(char *)(lVar4 + 0x142) == '\0') {
          local_res18 = 0;
          auStack_40[0] = 0x180434247;
          FUN_1804fd490((int)*(char *)(lVar9 + 10),lVar3,&local_res18);
          return local_res18;
        }
        auStack_40[0] = 0x1804341ab;
        iVar2 = strcmp(*(char **)(lVar4 + 0xa8),"Nullable`1");
        if (iVar2 == 0) {
          lVar7 = 0;
          do {
            lVar8 = lVar7 + 1;
            if (*(char *)(*(longlong *)(lVar4 + 0x20) + lVar7) != "System"[lVar7])
            goto LAB_1804341db;
            lVar7 = lVar8;
          } while (lVar8 != 7);
          lVar4 = *(longlong *)(lVar4 + 0x30);
          lVar9 = lVar4 + 0x60;
        }
LAB_1804341db:
        auStack_40[0] = 0x1804341e3;
        FUN_18044b5c0(lVar4);
        uVar6 = (ulonglong)*(uint *)(lVar4 + 0x114) - 1;
        if (uVar6 <= (ulonglong)*(uint *)(lVar4 + 0x114) - 0x10) {
          uVar6 = 0xffffffffffffff0;
        }
        auStack_40[0] = 0x18043420c;
        lVar7 = -(uVar6 & 0xfffffffffffffff0);
        cVar1 = *(char *)(lVar9 + 10);
        *(undefined8 *)((longlong)auStack_40 + lVar7) = 0x180434223;
        FUN_1804fd490((int)cVar1,lVar3,&stack0xffffffffffffffe8 + lVar7);
        *(undefined8 *)((longlong)auStack_40 + lVar7) = 0x18043422e;
        uVar5 = FUN_18042cf20(lVar4,&stack0xffffffffffffffe8 + lVar7);
        return uVar5;
      }
    }
  }
  return 0;
}



/* ================= 0x180434BD0 ================= */
/* name   = FUN_180434bd0 */
/* entry  = 180434bd0 */
/* body   = 98 bytes */
/* sig    = undefined FUN_180434bd0() */


longlong FUN_180434bd0(undefined8 param_1,undefined8 *param_2)

{
  int *piVar1;
  undefined8 uVar2;
  
  piVar1 = (int *)FUN_180434c40();
  if (piVar1 != (int *)0x0) {
    if (*piVar1 == -1) {
      uVar2 = 0;
    }
    else {
      uVar2 = *(undefined8 *)(PTR_PTR_1881a3628 + (longlong)*piVar1 * 8);
    }
    *param_2 = uVar2;
    if (piVar1[2] != -1) {
      return (longlong)piVar1[2] + ((longlong)DAT_188198e8c ^ 0x227cd810U) + DAT_1899dbaf8;
    }
  }
  return 0;
}



/* ================= 0x180435EE0 ================= */
/* name   = FUN_180435ee0 */
/* entry  = 180435ee0 */
/* body   = 25 bytes */
/* sig    = undefined FUN_180435ee0() */


undefined8 FUN_180435ee0(undefined8 param_1,undefined4 *param_2)

{
  FUN_180435f40(param_1,*param_2);
  return param_1;
}



/* ================= 0x180436030 ================= */
/* name   = FUN_180436030 */
/* entry  = 180436030 */
/* body   = 77 bytes */
/* sig    = undefined FUN_180436030() */


int FUN_180436030(undefined8 param_1)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  ushort *puVar4;
  ulonglong uVar5;
  
  puVar4 = (ushort *)FUN_1804f1130();
  uVar2 = FUN_1802bbf30(param_1);
  iVar3 = 0;
  if (0 < (int)uVar2) {
    uVar5 = (ulonglong)uVar2;
    do {
      uVar1 = *puVar4;
      puVar4 = puVar4 + 1;
      iVar3 = iVar3 * 0x1f + (uint)uVar1;
      uVar5 = uVar5 - 1;
    } while (uVar5 != 0);
  }
  return iVar3;
}



/* ================= 0x18043C530 ================= */
/* name   = FUN_18043c530 */
/* entry  = 18043c530 */
/* body   = 418 bytes */
/* sig    = undefined FUN_18043c530() */


/* WARNING: Function: _alloca_probe replaced with injection: alloca_probe */

undefined8 FUN_18043c530(longlong *param_1,longlong param_2,longlong param_3)

{
  int iVar1;
  longlong lVar2;
  ulonglong uVar3;
  int *piVar4;
  undefined8 uVar5;
  undefined1 *puVar6;
  longlong lVar7;
  undefined1 *puVar8;
  undefined8 local_res8;
  undefined8 uStack_40;
  undefined1 auStack_38 [32];
  
  puVar8 = auStack_38;
  uStack_40 = 0x18043c564;
  lVar2 = FUN_180430150(param_1[2] + -0x5a6601071b4f618a,1);
  if ((*(uint *)(param_1[2] + -0x5a6601071b4f6182) & 0x40) == 0) {
    if ((*(uint *)(param_1[2] + -0x5a6601071b4f6182) & 0x10) == 0) {
      puVar6 = (undefined1 *)((*(int *)((longlong)param_1 + 0x1c) + -0x7f804675) + param_2);
    }
    else if (*(int *)((longlong)param_1 + 0x1c) == 0x7f804674) {
      uStack_40 = 0x18043c65c;
      FUN_18042d860(*param_1 + -0x6381435a10901789);
      uStack_40 = 0x18043c664;
      iVar1 = FUN_18043afb0(param_1);
      puVar6 = (undefined1 *)
               ((longlong)iVar1 +
               *(longlong *)
                (*(longlong *)(*(longlong *)(param_3 + 0x10) + 0x60) +
                (longlong)*(int *)(*param_1 + -0x6381435a10901671) * 8));
      puVar8 = auStack_38;
    }
    else {
      uStack_40 = 0x18043c68b;
      FUN_18042d860(*param_1 + -0x6381435a10901789);
      puVar6 = (undefined1 *)
               ((longlong)(*(int *)((longlong)param_1 + 0x1c) + -0x7f804675) +
               *(longlong *)(*param_1 + -0x6381435a10901761));
      puVar8 = auStack_38;
    }
  }
  else {
    if (*(char *)(lVar2 + 0x142) == '\0') {
      lVar7 = 0;
      uStack_40 = 0x18043c5d7;
      piVar4 = (int *)FUN_180434c40(param_1);
      lVar2 = lVar7;
      if (piVar4 != (int *)0x0) {
        if (*piVar4 != -1) {
          lVar2 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)*piVar4 * 8);
        }
        if (piVar4[2] != -1) {
          lVar7 = ((longlong)DAT_188198e8c ^ 0x227cd810U) + DAT_1899dbaf8 + (longlong)piVar4[2];
        }
      }
      uStack_40 = 0x18043c626;
      FUN_1804fd490((int)*(char *)(lVar2 + 10),lVar7,&local_res8);
      return local_res8;
    }
    uVar3 = (ulonglong)*(uint *)(lVar2 + 0x114) - 1;
    if (uVar3 <= (ulonglong)*(uint *)(lVar2 + 0x114) - 0x10) {
      uVar3 = 0xffffffffffffff0;
    }
    uStack_40 = 0x18043c5b0;
    lVar7 = -(uVar3 & 0xfffffffffffffff0);
    puVar6 = &stack0xffffffffffffffe8 + lVar7;
    *(undefined8 *)(auStack_38 + lVar7 + -8) = 0x18043c5c3;
    FUN_180434070(param_1,puVar6);
    puVar8 = auStack_38 + lVar7;
  }
  *(undefined8 *)(puVar8 + -8) = 0x18043c6c2;
  uVar5 = FUN_18042cf20(lVar2,puVar6);
  return uVar5;
}



/* ================= 0x18044C170 ================= */
/* name   = FUN_18044c170 */
/* entry  = 18044c170 */
/* body   = 332 bytes */
/* sig    = undefined FUN_18044c170() */


void FUN_18044c170(longlong *param_1,undefined8 param_2)

{
  uint uVar1;
  undefined8 *puVar2;
  longlong lVar3;
  
  lVar3 = param_1[8];
  if (lVar3 != 0) {
    if (*(longlong *)(lVar3 + 0x10) != 0x129809a63f6f6527) {
      return;
    }
    if (lVar3 != 0) goto LAB_18044c1e9;
  }
  puVar2 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,1,0x18);
  if (puVar2 != (undefined8 *)0x0) {
    *puVar2 = 0x212364152c32f54b;
    puVar2[1] = 0x17c6f466730c70a9;
    puVar2[2] = 0x129809a63f6f6527;
  }
  param_1[8] = (longlong)puVar2;
LAB_18044c1e9:
  if (*(char *)((longlong)param_1 + 0x36) != '\0') {
    FUN_1804ee110(param_1,param_1[4]);
    return;
  }
  if (*(char *)(*param_1 + 0x131) == '\0') {
    uVar1 = *(int *)((ulonglong)*(uint *)(param_1 + 3) * 0x20 + 8 +
                    (DAT_188198e58 + -0x17a3b99) + DAT_1899dbaf8) + 0xaeae5feeU ^
            (uint)(((((ulonglong)*(uint *)(param_1 + 3) * 0xb069 ^ 0x3e382f2d) * 0x24147491 ^
                    0xf997b4a800) >> 10) * 0x3857aaca >> 0xe);
    if (uVar1 == 0xffffffff) {
      lVar3 = 0;
    }
    else {
      lVar3 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)(int)uVar1 * 8);
    }
    *(longlong *)(param_1[8] + 0x10) = lVar3 + 0x129809a63f6f6527;
    return;
  }
  FUN_1804ee090(param_1,param_2);
  return;
}



/* ================= 0x18044CE01 ================= */
/* name   = FUN_18044cde0 */
/* entry  = 18044cde0 */
/* body   = 1198 bytes */
/* sig    = undefined FUN_18044cde0() */


void FUN_18044cde0(longlong param_1,undefined8 param_2)

{
  uint uVar1;
  int iVar2;
  longlong lVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  longlong *plVar6;
  longlong lVar7;
  longlong lVar8;
  undefined8 *puVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  ulonglong uVar13;
  uint uVar14;
  
  if (*(char *)(param_1 + 0x140) == '\0') {
    if (*(undefined4 **)(param_1 + 0xc0) == (undefined4 *)0x0) {
      if (*(char *)(param_1 + 0x131) == '\0') {
        uVar10 = 0;
        if ((*(ushort *)(param_1 + 0x12e) != 0) && (*(longlong *)(param_1 + 0x70) == 0)) {
          uVar13 = (ulonglong)*(ushort *)(param_1 + 0x12e);
          puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar13,0x10);
          puVar9 = puVar4;
          for (; uVar13 != 0; uVar13 = uVar13 - 1) {
            if (puVar9 != (undefined8 *)0x0) {
              *puVar9 = 0;
              puVar9[1] = 0;
            }
            puVar9 = puVar9 + 2;
          }
          *(undefined8 **)(param_1 + 0x70) = puVar4;
          uVar11 = uVar10;
          if (*(short *)(param_1 + 0x12e) != 0) {
            do {
              uVar5 = *(undefined8 *)
                       (DAT_1899dbaf8 + (DAT_188198e80 + -0x1e7e75ad) +
                       (longlong)
                       (int)(((*(uint *)(*(longlong *)(param_1 + 0xd0) + 0x10) ^ 0x35eff672) -
                             *(int *)(param_1 + 200)) + (uint)uVar11) * 8);
              *(int *)(*(longlong *)(param_1 + 0x70) + 8 + (ulonglong)uVar11 * 0x10) =
                   (int)((ulonglong)uVar5 >> 0x20);
              lVar8 = 0;
              if ((int)uVar5 != -1) {
                lVar8 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)(int)uVar5 * 8);
              }
              uVar5 = FUN_180430150(lVar8,CONCAT71((uint7)((ulonglong)uVar5 >> 0x28),1));
              uVar12 = uVar11 + 1;
              *(undefined8 *)(*(longlong *)(param_1 + 0x70) + (ulonglong)uVar11 * 0x10) = uVar5;
              uVar11 = uVar12;
            } while (uVar12 < *(ushort *)(param_1 + 0x12e));
          }
        }
        if ((*(short *)(param_1 + 0x120) != 0) && (*(short *)(param_1 + 0x120) != 0)) {
          do {
            uVar1 = *(uint *)((DAT_188198e48 + -0x180a3d3b) + DAT_1899dbaf8 +
                             (longlong)
                             (int)(((*(uint *)(*(longlong *)(param_1 + 0xd0) + 8) ^ 0x5fa1c697) -
                                   *(int *)(param_1 + 200)) + (uint)uVar10) * 4);
            lVar8 = 0;
            if ((uVar1 & 0x1fffffff) != 0) {
              if ((uVar1 & 0xe0000000) == 0xc0000000) {
                uVar5 = FUN_180435e30();
                lVar8 = FUN_1804ebea0(uVar5,0);
              }
              else {
                lVar8 = FUN_180437120();
              }
            }
            *(longlong *)(param_1 + ((ulonglong)uVar10 + 0x15) * 0x10) = lVar8;
            if (lVar8 != 0) {
              *(undefined8 *)(param_1 + 0x148 + (ulonglong)uVar10 * 0x10) =
                   *(undefined8 *)(lVar8 + 8);
            }
            uVar10 = uVar10 + 1;
          } while (uVar10 < *(ushort *)(param_1 + 0x120));
        }
      }
      else {
        FUN_18043e550(*(undefined8 *)(param_1 + 0x30));
        FUN_1804edc20(param_1,param_2);
      }
    }
    else {
      lVar3 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
      lVar8 = *(longlong *)(param_1 + 0xc0);
      uVar10 = 0;
      if ((*(short *)(lVar3 + 0x12e) != 0) && (*(longlong *)(param_1 + 0x70) == 0)) {
        *(short *)(param_1 + 0x12e) = *(short *)(lVar3 + 0x12e);
        uVar13 = (ulonglong)*(ushort *)(lVar3 + 0x12e);
        puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar13,0x10);
        puVar9 = puVar4;
        for (; uVar13 != 0; uVar13 = uVar13 - 1) {
          if (puVar9 != (undefined8 *)0x0) {
            *puVar9 = 0;
            puVar9[1] = 0;
          }
          puVar9 = puVar9 + 2;
        }
        *(undefined8 **)(param_1 + 0x70) = puVar4;
        uVar11 = uVar10;
        if (*(short *)(lVar3 + 0x12e) != 0) {
          do {
            uVar13 = (ulonglong)uVar11;
            uVar5 = *(undefined8 *)
                     (DAT_1899dbaf8 + (DAT_188198e80 + -0x1e7e75ad) +
                     (longlong)
                     (int)(((*(uint *)(*(longlong *)(lVar3 + 0xd0) + 0x10) ^ 0x35eff672) -
                           *(int *)(lVar3 + 200)) + (uint)uVar11) * 8);
            *(int *)(uVar13 * 0x10 + 8 + *(longlong *)(param_1 + 0x70)) =
                 (int)((ulonglong)uVar5 >> 0x20);
            iVar2 = (int)uVar5;
            plVar6 = (longlong *)0x0;
            if (iVar2 != -1) {
              plVar6 = *(longlong **)(PTR_PTR_1881a3628 + (longlong)iVar2 * 8);
            }
            uVar5 = FUN_1804ecb50(plVar6,lVar8 + 8,0);
            uVar5 = FUN_180430150(uVar5,1);
            uVar11 = uVar11 + 1;
            *(undefined8 *)(uVar13 * 0x10 + *(longlong *)(param_1 + 0x70)) = uVar5;
          } while (uVar11 < *(ushort *)(lVar3 + 0x12e));
        }
      }
      if ((*(short *)(lVar3 + 0x120) != 0) &&
         (*(short *)(param_1 + 0x120) = *(short *)(lVar3 + 0x120), *(short *)(lVar3 + 0x120) != 0))
      {
        do {
          uVar1 = *(uint *)((DAT_188198e48 + -0x180a3d3b) + DAT_1899dbaf8 +
                           (longlong)
                           (int)(((*(uint *)(*(longlong *)(lVar3 + 0xd0) + 8) ^ 0x5fa1c697) -
                                 *(int *)(lVar3 + 200)) + (uint)uVar10) * 4);
          uVar14 = uVar1 & 0x1fffffff;
          plVar6 = (longlong *)0x0;
          if (uVar14 != 0) {
            if ((uVar1 & 0xe0000000) == 0xc0000000) {
              uVar5 = FUN_180435e30();
              plVar6 = (longlong *)FUN_1804ebea0(uVar5,0);
            }
            else {
              plVar6 = (longlong *)FUN_180437120(uVar14);
            }
          }
          if ((uVar1 & 0xe0000000) == 0xc0000000) {
            uVar5 = FUN_1804ec660(plVar6[4],lVar8 + 8);
LAB_18044d021:
            plVar6 = (longlong *)FUN_1804ebea0(uVar5,0);
          }
          else if ((plVar6 != (longlong *)0x0) && (*(char *)(*plVar6 + 0x13e) != '\0')) {
            uVar5 = FUN_180435c60(uVar14,*(undefined8 *)(lVar8 + 8),0);
            goto LAB_18044d021;
          }
          *(longlong **)(param_1 + ((ulonglong)uVar10 + 0x15) * 0x10) = plVar6;
          if (plVar6 != (longlong *)0x0) {
            lVar7 = plVar6[1];
            if (lVar7 == 0) {
              if (((*(char *)((longlong)plVar6 + 0x36) == '\0') ||
                  (*(char *)((longlong)plVar6 + 0x37) != '\0')) ||
                 (*(longlong *)(plVar6[4] + 0x10) != 0)) goto LAB_18044d070;
              lVar7 = FUN_18043c100();
            }
            *(longlong *)(param_1 + 0x148 + (ulonglong)uVar10 * 0x10) = lVar7;
          }
LAB_18044d070:
          uVar10 = uVar10 + 1;
        } while (uVar10 < *(ushort *)(lVar3 + 0x120));
      }
    }
    *(undefined1 *)(param_1 + 0x140) = 1;
  }
  return;
}



/* ================= 0x18044D08B ================= */
/* name   = FUN_18044cde0 */
/* entry  = 18044cde0 */
/* body   = 1198 bytes */
/* sig    = undefined FUN_18044cde0() */


void FUN_18044cde0(longlong param_1,undefined8 param_2)

{
  uint uVar1;
  int iVar2;
  longlong lVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  longlong *plVar6;
  longlong lVar7;
  longlong lVar8;
  undefined8 *puVar9;
  ushort uVar10;
  ushort uVar11;
  ushort uVar12;
  ulonglong uVar13;
  uint uVar14;
  
  if (*(char *)(param_1 + 0x140) == '\0') {
    if (*(undefined4 **)(param_1 + 0xc0) == (undefined4 *)0x0) {
      if (*(char *)(param_1 + 0x131) == '\0') {
        uVar10 = 0;
        if ((*(ushort *)(param_1 + 0x12e) != 0) && (*(longlong *)(param_1 + 0x70) == 0)) {
          uVar13 = (ulonglong)*(ushort *)(param_1 + 0x12e);
          puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar13,0x10);
          puVar9 = puVar4;
          for (; uVar13 != 0; uVar13 = uVar13 - 1) {
            if (puVar9 != (undefined8 *)0x0) {
              *puVar9 = 0;
              puVar9[1] = 0;
            }
            puVar9 = puVar9 + 2;
          }
          *(undefined8 **)(param_1 + 0x70) = puVar4;
          uVar11 = uVar10;
          if (*(short *)(param_1 + 0x12e) != 0) {
            do {
              uVar5 = *(undefined8 *)
                       (DAT_1899dbaf8 + (DAT_188198e80 + -0x1e7e75ad) +
                       (longlong)
                       (int)(((*(uint *)(*(longlong *)(param_1 + 0xd0) + 0x10) ^ 0x35eff672) -
                             *(int *)(param_1 + 200)) + (uint)uVar11) * 8);
              *(int *)(*(longlong *)(param_1 + 0x70) + 8 + (ulonglong)uVar11 * 0x10) =
                   (int)((ulonglong)uVar5 >> 0x20);
              lVar8 = 0;
              if ((int)uVar5 != -1) {
                lVar8 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)(int)uVar5 * 8);
              }
              uVar5 = FUN_180430150(lVar8,CONCAT71((uint7)((ulonglong)uVar5 >> 0x28),1));
              uVar12 = uVar11 + 1;
              *(undefined8 *)(*(longlong *)(param_1 + 0x70) + (ulonglong)uVar11 * 0x10) = uVar5;
              uVar11 = uVar12;
            } while (uVar12 < *(ushort *)(param_1 + 0x12e));
          }
        }
        if ((*(short *)(param_1 + 0x120) != 0) && (*(short *)(param_1 + 0x120) != 0)) {
          do {
            uVar1 = *(uint *)((DAT_188198e48 + -0x180a3d3b) + DAT_1899dbaf8 +
                             (longlong)
                             (int)(((*(uint *)(*(longlong *)(param_1 + 0xd0) + 8) ^ 0x5fa1c697) -
                                   *(int *)(param_1 + 200)) + (uint)uVar10) * 4);
            lVar8 = 0;
            if ((uVar1 & 0x1fffffff) != 0) {
              if ((uVar1 & 0xe0000000) == 0xc0000000) {
                uVar5 = FUN_180435e30();
                lVar8 = FUN_1804ebea0(uVar5,0);
              }
              else {
                lVar8 = FUN_180437120();
              }
            }
            *(longlong *)(param_1 + ((ulonglong)uVar10 + 0x15) * 0x10) = lVar8;
            if (lVar8 != 0) {
              *(undefined8 *)(param_1 + 0x148 + (ulonglong)uVar10 * 0x10) =
                   *(undefined8 *)(lVar8 + 8);
            }
            uVar10 = uVar10 + 1;
          } while (uVar10 < *(ushort *)(param_1 + 0x120));
        }
      }
      else {
        FUN_18043e550(*(undefined8 *)(param_1 + 0x30));
        FUN_1804edc20(param_1,param_2);
      }
    }
    else {
      lVar3 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
      lVar8 = *(longlong *)(param_1 + 0xc0);
      uVar10 = 0;
      if ((*(short *)(lVar3 + 0x12e) != 0) && (*(longlong *)(param_1 + 0x70) == 0)) {
        *(short *)(param_1 + 0x12e) = *(short *)(lVar3 + 0x12e);
        uVar13 = (ulonglong)*(ushort *)(lVar3 + 0x12e);
        puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar13,0x10);
        puVar9 = puVar4;
        for (; uVar13 != 0; uVar13 = uVar13 - 1) {
          if (puVar9 != (undefined8 *)0x0) {
            *puVar9 = 0;
            puVar9[1] = 0;
          }
          puVar9 = puVar9 + 2;
        }
        *(undefined8 **)(param_1 + 0x70) = puVar4;
        uVar11 = uVar10;
        if (*(short *)(lVar3 + 0x12e) != 0) {
          do {
            uVar13 = (ulonglong)uVar11;
            uVar5 = *(undefined8 *)
                     (DAT_1899dbaf8 + (DAT_188198e80 + -0x1e7e75ad) +
                     (longlong)
                     (int)(((*(uint *)(*(longlong *)(lVar3 + 0xd0) + 0x10) ^ 0x35eff672) -
                           *(int *)(lVar3 + 200)) + (uint)uVar11) * 8);
            *(int *)(uVar13 * 0x10 + 8 + *(longlong *)(param_1 + 0x70)) =
                 (int)((ulonglong)uVar5 >> 0x20);
            iVar2 = (int)uVar5;
            plVar6 = (longlong *)0x0;
            if (iVar2 != -1) {
              plVar6 = *(longlong **)(PTR_PTR_1881a3628 + (longlong)iVar2 * 8);
            }
            uVar5 = FUN_1804ecb50(plVar6,lVar8 + 8,0);
            uVar5 = FUN_180430150(uVar5,1);
            uVar11 = uVar11 + 1;
            *(undefined8 *)(uVar13 * 0x10 + *(longlong *)(param_1 + 0x70)) = uVar5;
          } while (uVar11 < *(ushort *)(lVar3 + 0x12e));
        }
      }
      if ((*(short *)(lVar3 + 0x120) != 0) &&
         (*(short *)(param_1 + 0x120) = *(short *)(lVar3 + 0x120), *(short *)(lVar3 + 0x120) != 0))
      {
        do {
          uVar1 = *(uint *)((DAT_188198e48 + -0x180a3d3b) + DAT_1899dbaf8 +
                           (longlong)
                           (int)(((*(uint *)(*(longlong *)(lVar3 + 0xd0) + 8) ^ 0x5fa1c697) -
                                 *(int *)(lVar3 + 200)) + (uint)uVar10) * 4);
          uVar14 = uVar1 & 0x1fffffff;
          plVar6 = (longlong *)0x0;
          if (uVar14 != 0) {
            if ((uVar1 & 0xe0000000) == 0xc0000000) {
              uVar5 = FUN_180435e30();
              plVar6 = (longlong *)FUN_1804ebea0(uVar5,0);
            }
            else {
              plVar6 = (longlong *)FUN_180437120(uVar14);
            }
          }
          if ((uVar1 & 0xe0000000) == 0xc0000000) {
            uVar5 = FUN_1804ec660(plVar6[4],lVar8 + 8);
LAB_18044d021:
            plVar6 = (longlong *)FUN_1804ebea0(uVar5,0);
          }
          else if ((plVar6 != (longlong *)0x0) && (*(char *)(*plVar6 + 0x13e) != '\0')) {
            uVar5 = FUN_180435c60(uVar14,*(undefined8 *)(lVar8 + 8),0);
            goto LAB_18044d021;
          }
          *(longlong **)(param_1 + ((ulonglong)uVar10 + 0x15) * 0x10) = plVar6;
          if (plVar6 != (longlong *)0x0) {
            lVar7 = plVar6[1];
            if (lVar7 == 0) {
              if (((*(char *)((longlong)plVar6 + 0x36) == '\0') ||
                  (*(char *)((longlong)plVar6 + 0x37) != '\0')) ||
                 (*(longlong *)(plVar6[4] + 0x10) != 0)) goto LAB_18044d070;
              lVar7 = FUN_18043c100();
            }
            *(longlong *)(param_1 + 0x148 + (ulonglong)uVar10 * 0x10) = lVar7;
          }
LAB_18044d070:
          uVar10 = uVar10 + 1;
        } while (uVar10 < *(ushort *)(lVar3 + 0x120));
      }
    }
    *(undefined1 *)(param_1 + 0x140) = 1;
  }
  return;
}



