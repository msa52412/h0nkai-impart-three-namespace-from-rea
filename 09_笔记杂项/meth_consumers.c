// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 1804361a0 ================= */
/* name   = FUN_1804361a0 */
/* entry  = 1804361a0 */
/* body   = 527 bytes */
/* sig    = undefined FUN_1804361a0() */


void FUN_1804361a0(longlong param_1,longlong *param_2,longlong param_3,uint param_4)

{
  char cVar1;
  char cVar2;
  longlong lVar3;
  char *pcVar4;
  longlong lVar5;
  longlong lVar6;
  ulonglong uVar7;
  longlong *plVar8;
  longlong lVar9;
  uint uVar10;
  undefined *local_res8;
  
  lVar9 = (longlong)(int)param_4;
  if ((*(short *)(param_1 + 0x124) != 0) || (*(char *)(param_1 + 0x131) != '\0')) {
    local_res8 = &DAT_1899db6b0;
    FUN_1803f4990();
    FUN_18044c400(param_1,&local_res8);
    FUN_1803f72c0(local_res8);
  }
  if (*(longlong *)(param_1 + 0x18) != 0) {
    if ((*(longlong *)(param_1 + 0xc0) == 0) && (*(char *)(param_1 + 0x131) == '\0')) {
      uVar10 = (*(int *)(*(longlong *)(param_1 + 0xd0) + 0x14) - *(int *)(param_1 + 200)) +
               0xd7dd4afe;
      lVar9 = (longlong)(int)(*(ushort *)(param_1 + 0x124) + uVar10);
      if ((int)uVar10 < lVar9) {
        lVar6 = 0;
        lVar9 = lVar9 - (int)uVar10;
        do {
          uVar7 = ((((ulonglong)uVar10 * 0xb069 ^ 0x3e382f2d) * 0x24147491 ^ 0xf997b4a800) >> 10) *
                  0x3857aaca >> 0xe;
          lVar5 = (ulonglong)uVar10 * 0x20;
          lVar3 = (DAT_188198e58 + -0x17a3b99) + DAT_1899dbaf8;
          if ((((*(char *)(lVar5 + 0x1c + lVar3) - 0x10U ^ (byte)uVar7) & 0x10) == 0) &&
             (lVar3 = FUN_18043ab50(*(uint *)(lVar5 + 0xc + lVar3) ^ (uint)uVar7 ^ 0x1d64b276),
             0 < (int)param_4)) {
            uVar7 = (ulonglong)param_4;
            plVar8 = param_2;
            do {
              pcVar4 = *(char **)((param_3 - (longlong)param_2) + (longlong)plVar8);
              if ((pcVar4 != (char *)0x0) && (*plVar8 == 0)) {
                lVar5 = lVar3 - (longlong)pcVar4;
                do {
                  cVar1 = *pcVar4;
                  cVar2 = pcVar4[lVar5];
                  if (cVar1 != cVar2) break;
                  pcVar4 = pcVar4 + 1;
                } while (cVar2 != '\0');
                if (cVar1 == cVar2) {
                  *plVar8 = *(longlong *)(lVar6 + *(longlong *)(param_1 + 0x18));
                }
              }
              plVar8 = plVar8 + 1;
              uVar7 = uVar7 - 1;
            } while (uVar7 != 0);
          }
          uVar10 = uVar10 + 1;
          lVar6 = lVar6 + 8;
          lVar9 = lVar9 + -1;
        } while (lVar9 != 0);
      }
    }
    else if (0 < (int)param_4) {
      param_3 = param_3 - (longlong)param_2;
      do {
        if (*param_2 == 0) {
          lVar6 = FUN_180436f50(param_1,*(undefined8 *)((longlong)param_2 + param_3),0,0x10,0);
          *param_2 = lVar6;
        }
        param_2 = param_2 + 1;
        lVar9 = lVar9 + -1;
      } while (lVar9 != 0);
    }
  }
  return;
}



/* ================= 1804398b0 ================= */
/* name   = FUN_1804398b0 */
/* entry  = 1804398b0 */
/* body   = 217 bytes */
/* sig    = undefined FUN_1804398b0() */


int * FUN_1804398b0(longlong param_1,longlong param_2)

{
  int *piVar1;
  uint uVar2;
  int *piVar3;
  
  if ((*(char *)(param_1 + 0x36) != '\0') && (*(char *)(param_1 + 0x37) == '\0')) {
    param_1 = FUN_180437120(**(undefined4 **)(param_1 + 0x20));
  }
  uVar2 = *(uint *)(param_1 + 0x18);
  if (uVar2 != 0xffffffff) {
    piVar3 = (int *)(((longlong)DAT_188198e7c ^ 0x2a721817U) + DAT_1899dbaf8);
    piVar1 = piVar3 + ((longlong)DAT_188198e54 ^ 0x6a0bfd5dU) * 3;
    for (; piVar3 < piVar1; piVar3 = piVar3 + 3) {
      if ((*(int *)((ulonglong)uVar2 * 0x20 + 4 + (DAT_188198e58 + -0x17a3b99) + DAT_1899dbaf8) +
           0xea530370U ^
          (uint)(((((ulonglong)uVar2 * 0xb069 ^ 0x3e382f2d) * 0x24147491 ^ 0xf997b4a800) >> 10) *
                 0x3857aaca >> 0xe)) + *(int *)(param_2 + 0x14) == *piVar3) {
        return piVar3;
      }
    }
  }
  return (int *)0x0;
}



/* ================= 18044bf61 ================= */
/* name   = FUN_18044beb0 */
/* entry  = 18044beb0 */
/* body   = 696 bytes */
/* sig    = undefined FUN_18044beb0() */


void FUN_18044beb0(longlong *param_1,undefined8 param_2)

{
  int *piVar1;
  uint uVar2;
  undefined8 *puVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  longlong lVar6;
  ulonglong uVar7;
  ushort uVar8;
  uint uVar9;
  ulonglong uVar10;
  longlong lVar11;
  uint *puVar12;
  
  lVar11 = param_1[8];
  if (lVar11 != 0) {
    if (*(longlong *)(lVar11 + 8) != 0x17c6f466730c70a9) {
      return;
    }
    if (lVar11 != 0) goto LAB_18044bf27;
  }
  puVar3 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,1,0x18);
  if (puVar3 != (undefined8 *)0x0) {
    *puVar3 = 0x212364152c32f54b;
    puVar3[1] = 0x17c6f466730c70a9;
    puVar3[2] = 0x129809a63f6f6527;
  }
  param_1[8] = (longlong)puVar3;
LAB_18044bf27:
  if (*(char *)((longlong)param_1 + 0x36) != '\0') {
    FUN_1804ee000(param_1,param_1[4]);
    return;
  }
  if (*(char *)(*param_1 + 0x131) == '\0') {
    lVar11 = (ulonglong)*(uint *)(param_1 + 3) * 0x20 + (DAT_188198e58 + -0x17a3b99) + DAT_1899dbaf8
    ;
    uVar10 = ((((ulonglong)*(uint *)(param_1 + 3) * 0xb069 ^ 0x3e382f2d) * 0x24147491 ^ 0xf997b4a800
              ) >> 10) * 0x3857aaca >> 0xe;
    uVar7 = (ulonglong)(ushort)(*(short *)(lVar11 + 0x1a) + 0x2641) ^ uVar10 & 0xffff;
    puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar7,0x18);
    puVar3 = puVar4;
    for (; uVar7 != 0; uVar7 = uVar7 - 1) {
      if (puVar3 != (undefined8 *)0x0) {
        *puVar3 = 0;
        puVar3[1] = 0;
        puVar3[2] = 0;
      }
      puVar3 = puVar3 + 3;
    }
    uVar8 = 0;
    if ((ushort)(*(short *)(lVar11 + 0x1a) + 0x2641U) != (ushort)uVar10) {
      puVar12 = (uint *)((longlong)puVar4 + 0x14);
      do {
        uVar2 = (*(int *)(lVar11 + 4) + 0xea530370U ^ (uint)uVar10) + (uint)uVar8;
        lVar6 = ((longlong)DAT_188198e30 ^ 0x7ea603b1U) + DAT_1899dbaf8;
        piVar1 = (int *)(lVar6 + (ulonglong)uVar2 * 0xc);
        uVar9 = (int)(((ulonglong)uVar2 * 0x90c17665df3 + 0x125f81ccd2df4209 ^ 0x390acbf7) *
                      0x7babb4a2 >> 0xf) + 0x476926e5;
        uVar5 = FUN_18043ab50(*(uint *)(lVar6 + 4 + (ulonglong)uVar2 * 0xc) ^ uVar9 ^ 0x4cc553b0);
        *(undefined8 *)(puVar12 + -3) = uVar5;
        *puVar12 = (uint)uVar8;
        puVar12[-1] = piVar1[2] ^ uVar9 ^ 0x6697d2d9;
        uVar9 = *piVar1 + 0xc6f108a2U ^ uVar9;
        if (uVar9 == 0xffffffff) {
          uVar5 = 0;
        }
        else {
          uVar5 = *(undefined8 *)(PTR_PTR_1881a3628 + (longlong)(int)uVar9 * 8);
        }
        *(undefined8 *)(puVar12 + -5) = uVar5;
        uVar8 = uVar8 + 1;
        puVar12 = puVar12 + 6;
      } while (uVar8 < (ushort)(*(short *)(lVar11 + 0x1a) + 0x2641U ^ (ushort)uVar10));
    }
    *(longlong *)(param_1[8] + 8) = (longlong)puVar4 + 0x17c6f466730c70a9;
    return;
  }
  FUN_1804edf70(param_1,param_2);
  return;
}



/* ================= 18044c170 ================= */
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



/* ================= 18044c55e ================= */
/* name   = FUN_18044c400 */
/* entry  = 18044c400 */
/* body   = 926 bytes */
/* sig    = undefined FUN_18044c400() */


void FUN_18044c400(longlong param_1,undefined8 param_2)

{
  longlong *plVar1;
  int iVar2;
  undefined8 uVar3;
  undefined8 *puVar4;
  longlong lVar5;
  uint uVar6;
  undefined8 *puVar7;
  ulonglong uVar8;
  longlong *plVar9;
  longlong lVar10;
  ushort uVar11;
  uint uVar12;
  uint uVar13;
  longlong lVar14;
  longlong local_res18;
  
  uVar11 = *(ushort *)(param_1 + 0x124);
  if (((uVar11 != 0) || (*(char *)(param_1 + 0x131) != '\0')) &&
     (*(longlong *)(param_1 + 0x18) == 0)) {
    if (*(undefined4 **)(param_1 + 0xc0) != (undefined4 *)0x0) {
      uVar3 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
      FUN_18044c400(uVar3,param_2);
      FUN_18044c320(param_1);
      return;
    }
    if (*(char *)(param_1 + 0x131) != '\0') {
      FUN_18043e550(*(undefined8 *)(param_1 + 0x30));
      FUN_18044cde0(param_1,param_2);
      return;
    }
    if (uVar11 == 0) {
      *(undefined8 *)(param_1 + 0x18) = 0;
      return;
    }
    uVar8 = (ulonglong)uVar11;
    puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar8,8);
    puVar7 = puVar4;
    for (; uVar8 != 0; uVar8 = uVar8 - 1) {
      if (puVar7 != (undefined8 *)0x0) {
        *puVar7 = 0;
      }
      puVar7 = puVar7 + 1;
    }
    uVar8 = (ulonglong)*(ushort *)(param_1 + 0x124);
    *(undefined8 **)(param_1 + 0x18) = puVar4;
    puVar4 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar8,0x48);
    puVar7 = puVar4;
    for (; uVar8 != 0; uVar8 = uVar8 - 1) {
      if (puVar7 != (undefined8 *)0x0) {
        *puVar7 = 0;
        puVar7[1] = 0;
        puVar7[2] = 0;
        puVar7[3] = 0;
        puVar7[4] = 0;
        puVar7[5] = 0;
        puVar7[6] = 0;
        puVar7[7] = 0;
        puVar7[8] = 0;
      }
      puVar7 = puVar7 + 9;
    }
    uVar13 = (*(int *)(*(longlong *)(param_1 + 0xd0) + 0x14) - *(int *)(param_1 + 200)) + 0xd7dd4afe
    ;
    lVar14 = (longlong)(int)(*(ushort *)(param_1 + 0x124) + uVar13);
    if ((int)uVar13 < lVar14) {
      lVar14 = lVar14 - (int)uVar13;
      plVar9 = puVar4 + 1;
      local_res18 = 0;
      do {
        uVar8 = ((((ulonglong)uVar13 * 0xb069 ^ 0x3e382f2d) * 0x24147491 ^ 0xf997b4a800) >> 10) *
                0x3857aaca >> 0xe;
        lVar10 = (ulonglong)uVar13 * 0x20 + (DAT_188198e58 + -0x17a3b99) + DAT_1899dbaf8;
        uVar12 = (uint)uVar8;
        if ((*(char *)(param_1 + 0x142) != '\0') &&
           (lVar5 = FUN_180431710(*(undefined8 *)(param_1 + 0x58),
                                  *(int *)(lVar10 + 0x14) + 0xbd6fc398U ^ uVar12), lVar5 != 0)) {
          *plVar9 = lVar5;
        }
        if (*plVar9 == 0) {
          uVar6 = (*(int *)(lVar10 + 0x14) + 0x6fc398U ^ uVar12) & 0xffffff;
          if (uVar6 == 0) {
            lVar5 = 0;
          }
          else {
            lVar5 = *(longlong *)
                     (*(longlong *)
                       (*(longlong *)(*(longlong *)(param_1 + 0x58) + 0x30) + -0x15efe0164a2ec173) +
                     (ulonglong)(uVar6 - 1) * 8);
          }
          *plVar9 = lVar5;
        }
        plVar9[-1] = param_1;
        plVar1 = plVar9 + -1;
        *(uint *)(plVar9 + 2) = uVar13;
        *(uint *)(plVar9 + 3) = *(uint *)(lVar10 + 0x10) ^ uVar12 ^ 0x1a57a870;
        uVar6 = (*(int *)(lVar10 + 0x14) + 0x6fc398U ^ uVar12) & 0xffffff;
        if (uVar6 == 0) {
          lVar5 = 0;
        }
        else {
          iVar2 = *(int *)(*(longlong *)
                            (*(longlong *)(*(longlong *)(param_1 + 0x58) + 0x30) +
                            -0x15efe0164a2ec14b) + (ulonglong)(uVar6 - 1) * 4);
          if (iVar2 == -1) {
            lVar5 = 0;
          }
          else {
            lVar5 = *(longlong *)(PTR_PTR_188139718 + (longlong)iVar2 * 8);
          }
        }
        plVar9[1] = lVar5;
        *(uint *)(plVar9 + 4) = *(int *)(lVar10 + 0x14) + 0xbd6fc398U ^ uVar12;
        uVar11 = (ushort)uVar8;
        *(ushort *)((longlong)plVar9 + 0x26) = *(short *)(lVar10 + 0x1c) + 0xdab0U ^ uVar11;
        *(ushort *)((longlong)plVar9 + 0x24) = *(ushort *)(lVar10 + 0x1e) ^ uVar11 ^ 0x4d12;
        *(ushort *)(plVar9 + 5) = *(short *)(lVar10 + 0x18) + 0xac47U ^ uVar11;
        *(byte *)((longlong)plVar9 + 0x2a) = *(char *)(lVar10 + 0x1a) + 0x41U ^ (byte)uVar8;
        if ((int)plVar9[3] != -1) {
          *(undefined1 *)((longlong)plVar9 + 0x2f) = 1;
        }
        *(undefined1 *)((longlong)plVar9 + 0x2e) = 0;
        if (((*(short *)(lVar10 + 0x1c) - 0x550U ^ uVar11) & 0x1000) != 0) {
          *(bool *)((longlong)plVar9 + 0x2c) =
               (uVar12 ^ *(uint *)(lVar10 + 0xc) ^ 0x1d64b276) == DAT_188198df8;
          *(bool *)((longlong)plVar9 + 0x2d) =
               (uVar12 ^ *(uint *)(lVar10 + 0xc) ^ 0x1d64b276) == DAT_188198dfc;
        }
        uVar13 = uVar13 + 1;
        plVar9 = plVar9 + 9;
        *(longlong **)(local_res18 + *(longlong *)(param_1 + 0x18)) = plVar1;
        local_res18 = local_res18 + 8;
        lVar14 = lVar14 + -1;
      } while (lVar14 != 0);
    }
  }
  return;
}



/* ================= 18043ec20 ================= */
/* name   = FUN_18043ec20 */
/* entry  = 18043ec20 */
/* body   = 3437 bytes */
/* sig    = undefined FUN_18043ec20() */


undefined8 FUN_18043ec20(void)

{
  char cVar1;
  char cVar2;
  undefined1 auVar3 [16];
  int iVar4;
  int iVar5;
  longlong lVar6;
  char *pcVar7;
  longlong lVar8;
  undefined8 *puVar9;
  undefined8 *puVar10;
  char ****ppppcVar11;
  uint *puVar12;
  ulonglong uVar13;
  undefined4 *puVar14;
  int *piVar15;
  uint *puVar16;
  int *piVar17;
  ushort uVar18;
  ulonglong uVar19;
  ulonglong uVar20;
  uint uVar21;
  ulonglong uVar22;
  uint uVar23;
  longlong lVar24;
  short sVar25;
  undefined4 uVar26;
  undefined4 uVar27;
  undefined4 uVar28;
  longlong local_res8;
  ulonglong local_res10;
  longlong local_res18;
  undefined8 *local_2b8;
  undefined8 *puStack_2b0;
  undefined8 *local_2a8;
  undefined8 local_2a0;
  int iStack_298;
  undefined4 uStack_294;
  undefined8 local_290;
  ulonglong local_288;
  char ***local_280 [2];
  longlong local_270;
  ulonglong local_268;
  undefined8 local_260;
  uint local_258;
  CHAR local_248 [520];
  
  local_260 = 0xfffffffffffffffe;
  lVar6 = FUN_180443fc0();
  FUN_1804ed510(DAT_1881396ac);
  DAT_1899dbaf8 = lVar6 + 0x118;
  if (*(int *)(lVar6 + 4) != DAT_188198df4) {
    FUN_1803faa80(local_248,"dll version(%d) and metadata version(%d) is not math");
    MessageBoxA((HWND)0x0,local_248,"Error",0);
                    /* WARNING: Subroutine does not return */
    FUN_180510c38();
  }
  lVar6 = (longlong)(int)(DAT_1881a3640 ^ 0x7cd3b5b8);
  DAT_1899dbbe8 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,lVar6,8);
  uVar19 = 0;
  puVar9 = DAT_1899dbbe8;
  for (; lVar6 != 0; lVar6 = lVar6 + -1) {
    if (puVar9 != (undefined8 *)0x0) {
      *puVar9 = 0;
    }
    puVar9 = puVar9 + 1;
  }
  auVar3._8_8_ = 0;
  auVar3._0_8_ = (longlong)(DAT_188198e78 + -0xa4ffd99);
  lVar6 = SUB168(ZEXT816(0x642c8590b21642c9) * auVar3,8);
  uVar13 = ((ulonglong)((DAT_188198e78 + -0xa4ffd99) - lVar6) >> 1) + lVar6 >> 6;
  DAT_1899dbbf0 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar13,8);
  puVar9 = DAT_1899dbbf0;
  for (; uVar13 != 0; uVar13 = uVar13 - 1) {
    if (puVar9 != (undefined8 *)0x0) {
      *puVar9 = 0;
    }
    puVar9 = puVar9 + 1;
  }
  uVar13 = (ulonglong)(longlong)(int)(DAT_188198e14 ^ 0x5f613838) >> 5;
  DAT_1899dbbf8 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,uVar13,8);
  puVar9 = DAT_1899dbbf8;
  for (; uVar13 != 0; uVar13 = uVar13 - 1) {
    if (puVar9 != (undefined8 *)0x0) {
      *puVar9 = 0;
    }
    puVar9 = puVar9 + 1;
  }
  lVar6 = (longlong)(int)(DAT_1881a35ec ^ 0x7cc59670);
  DAT_1899dbc00 = (undefined8 *)FUN_1804f09a0(DAT_1899dbad0,lVar6,8);
  puVar9 = DAT_1899dbc00;
  for (; lVar6 != 0; lVar6 = lVar6 + -1) {
    if (puVar9 != (undefined8 *)0x0) {
      *puVar9 = 0;
    }
    puVar9 = puVar9 + 1;
  }
  DAT_1899dbc08 = (int)((ulonglong)(longlong)(int)(DAT_188198e4c ^ 0x6f3f9184) / 0x28);
  uVar13 = (ulonglong)DAT_1899dbc08;
  lVar6 = FUN_1804f09a0(DAT_1899dbad0,uVar13,0x50);
  if (uVar13 != 0) {
    do {
      puVar14 = (undefined4 *)(uVar19 * 0x50 + lVar6);
      if (puVar14 != (undefined4 *)0x0) {
        FUN_180500080(puVar14,0,0x50);
        *puVar14 = 0x188fa8da;
        puVar14[1] = 0x5887c8c6;
        puVar14[4] = 0x223ca3b8;
        puVar14[5] = 0x1d3b2899;
        puVar14[6] = 0x61a2155e;
        puVar14[7] = 0x53c69178;
        puVar14[8] = 0x3a0aaefe;
        *(undefined8 *)(puVar14 + 10) = 0x3f10e1615e5443f4;
        *(undefined8 *)(puVar14 + 0xc) = 0x15efe0164a2ec19b;
        *(undefined8 *)(puVar14 + 0xe) = 0x563412751289b3d9;
        puVar14[0x10] = 0x27fd9462;
        *(undefined8 *)(puVar14 + 0x12) = 0x459dcf922742193b;
      }
      uVar19 = uVar19 + 1;
    } while (uVar19 < uVar13);
  }
  uVar13 = 0;
  DAT_1899dbc18 = (int)((ulonglong)(longlong)(int)(DAT_188198e20 ^ 0x20910e12) >> 4);
  uVar19 = (ulonglong)DAT_1899dbc18;
  DAT_1899dbc10 = lVar6;
  lVar6 = FUN_1804f09a0(DAT_1899dbad0);
  if (uVar19 != 0) {
    do {
      puVar14 = (undefined4 *)(uVar13 * 0x60 + lVar6);
      if (puVar14 != (undefined4 *)0x0) {
        FUN_180500080(puVar14);
        *puVar14 = 0x76cb3b6d;
        *(undefined8 *)(puVar14 + 2) = 0x56ead61b43cc4f04;
        puVar14[4] = 0x23e109de;
        puVar14[6] = 0x39fd8dcc;
        puVar14[7] = 0x448ae27e;
        puVar14[8] = 0x2779c1dd;
        puVar14[9] = 0x28f01ff2;
        puVar14[10] = 0x6b612990;
        *(undefined8 *)(puVar14 + 0xc) = 0x6a690e5722724657;
        puVar14[0xe] = 0x4fbc7cff;
        *(undefined8 *)(puVar14 + 0x10) = 0x6308e3be1d7e78d0;
        puVar14[0x12] = 0x41e927b0;
        puVar14[0x16] = 0x7a6bdaca;
      }
      uVar13 = uVar13 + 1;
    } while (uVar13 < uVar19);
  }
  uVar13 = 0;
  lVar24 = (int)(DAT_188198e1c ^ 0x72267500) + DAT_1899dbaf8;
  uVar22 = 0;
  uVar19 = uVar13;
  DAT_1899dbc20 = lVar6;
  if (0 < DAT_1899dbc08) {
    do {
      piVar17 = (int *)(uVar22 * 0x28 + lVar24);
      piVar15 = (int *)(DAT_1899dbc10 + uVar19);
      iVar5 = (int)(((uVar22 * 0x14c3bd9234d3 >> 9) + 0x48c65e21) * 0x22343ddf >> 0x15);
      pcVar7 = (char *)FUN_18043ab50((piVar17[5] + -0x3d7dc690) - iVar5);
      *(char **)(piVar15 + 0x12) = pcVar7 + 0x459dcf922742193b;
      local_288 = 0xf;
      local_290 = 0;
      local_2a0 = local_2a0 & 0xffffffffffffff00;
      uVar20 = uVar13;
      if (*pcVar7 != '\0') {
        uVar20 = 0xffffffffffffffff;
        do {
          uVar20 = uVar20 + 1;
        } while (pcVar7[uVar20] != '\0');
      }
      FUN_1803f92e0(&local_2a0,pcVar7,uVar20);
      FUN_1804f1770(local_280,&local_2a0);
      if (0xf < local_288) {
        uVar20 = local_2a0;
        if (0xfff < local_288 + 1) {
          if ((local_2a0 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar20 = *(ulonglong *)(local_2a0 - 8);
          if (local_2a0 <= uVar20) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (local_2a0 - uVar20 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < local_2a0 - uVar20) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar20);
      }
      local_288 = 0xf;
      local_290 = 0;
      local_2a0 = local_2a0 & 0xffffffffffffff00;
      pcVar7 = (char *)_calloc_base(local_270 + 1,1);
      *(ulonglong *)(piVar15 + 10) = (ulonglong)pcVar7 ^ 0x3f10e1615e5443f4;
      ppppcVar11 = local_280;
      if (0xf < local_268) {
        ppppcVar11 = (char ****)local_280[0];
      }
      do {
        cVar1 = *(char *)ppppcVar11;
        *pcVar7 = cVar1;
        pcVar7 = pcVar7 + 1;
        ppppcVar11 = (char ****)((longlong)ppppcVar11 + 1);
      } while (cVar1 != '\0');
      iVar4 = (piVar17[6] + -0x12813d35) - iVar5;
      uVar20 = uVar13;
      if (iVar4 != -1) {
        uVar20 = (longlong)iVar4 * 0x60 + DAT_1899dbc20;
      }
      *(ulonglong *)(piVar15 + 0xe) = uVar20 ^ 0x563412751289b3d9;
      piVar15[5] = (piVar17[8] + -0x3d2e6fe3) - iVar5 ^ 0x1d3b2899;
      piVar15[7] = (piVar17[4] + -0x7c293e16) - iVar5 ^ 0x53c69178;
      *piVar15 = (piVar17[3] - iVar5) + -0x3640f13b;
      piVar15[6] = (*piVar17 + -0x36d7455a) - iVar5 ^ 0x61a2155e;
      piVar15[8] = ((piVar17[7] ^ 0x16a0e2a5U) - iVar5) + 0x3a0aaefe;
      piVar15[0x10] = ((piVar17[9] ^ 0xca5b561U) - iVar5) + 0x27fd9462;
      piVar15[4] = (piVar17[1] - iVar5) + 0x1298b083;
      piVar15[1] = (piVar17[2] + -0x3b4b92fd) - iVar5 ^ 0x5887c8c6;
      uVar20 = 0;
      iVar5 = DAT_1881396d8;
      if (DAT_1881396d8 != 0x18a8540c) {
        do {
          pcVar7 = (char *)(*(longlong *)(piVar15 + 0x12) + -0x459dcf922742193b);
          lVar6 = *(longlong *)(*(longlong *)(PTR_PTR_1881396f8 + uVar20 * 8) + 0x48) -
                  (longlong)pcVar7;
          do {
            cVar1 = *pcVar7;
            cVar2 = pcVar7[lVar6];
            if (cVar1 != cVar2) break;
            pcVar7 = pcVar7 + 1;
          } while (cVar2 != '\0');
          if (cVar1 == cVar2) {
            *(longlong *)(piVar15 + 0xc) =
                 *(longlong *)(PTR_PTR_1881396f8 + uVar20 * 8) + 0x15efe0164a2ec19b;
            iVar5 = DAT_1881396d8;
          }
          uVar21 = (int)uVar20 + 1;
          uVar20 = (ulonglong)uVar21;
        } while (uVar21 < iVar5 + 0xe757abf4U);
      }
      if (0xf < local_268) {
        ppppcVar11 = (char ****)local_280[0];
        if (0xfff < local_268 + 1) {
          if (((ulonglong)local_280[0] & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          ppppcVar11 = (char ****)local_280[0][-1];
          if (local_280[0] <= ppppcVar11) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if ((ulonglong)((longlong)local_280[0] - (longlong)ppppcVar11) < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < (ulonglong)((longlong)local_280[0] - (longlong)ppppcVar11)) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(ppppcVar11);
      }
      uVar21 = (int)uVar22 + 1;
      uVar22 = (ulonglong)uVar21;
      uVar19 = uVar19 + 0x50;
    } while ((int)uVar21 < DAT_1899dbc08);
  }
  lVar24 = (int)(DAT_188198e60 ^ 0x371b8070) + DAT_1899dbaf8;
  lVar6 = (int)(DAT_188198e70 ^ 0x561c6fd) + DAT_1899dbaf8;
  uVar19 = 0;
  if (0 < DAT_1899dbc08) {
    local_res8 = 0;
    do {
      iVar4 = (int)uVar19;
      uVar21 = (iVar4 * 0x56184a41 + 0x57a94b1fU ^ 0x37f164b8) * 0x10fb44e5 ^ 0x7b1de297;
      puVar12 = (uint *)(uVar19 * 0x10 + lVar24);
      uVar23 = (iVar4 * 0x447fce41 ^ 0x120dd35fU) * 0x3e8906da;
      puVar16 = (uint *)(uVar19 * 0x2c + lVar6);
      piVar15 = (int *)(DAT_1899dbc20 + local_res8);
      iVar5 = (puVar12[2] + 0xfc36a893) - uVar21;
      uVar19 = uVar13;
      if (iVar5 != -1) {
        uVar19 = (longlong)iVar5 * 0x50 + DAT_1899dbc10;
      }
      *(ulonglong *)(piVar15 + 2) = uVar19 ^ 0x56ead61b43cc4f04;
      piVar15[4] = ((*puVar12 ^ 0x6e35edff) - uVar21) + 0x23e109de;
      piVar15[0x16] = (puVar12[1] ^ 0x242d7f7e) - uVar21 ^ 0x7a6bdaca;
      *piVar15 = ((puVar12[3] ^ 0x755539f1) - uVar21) + 0x76cb3b6d;
      lVar8 = FUN_18043ab50(puVar16[1] + 0x84b0104a ^ uVar23);
      *(longlong *)(piVar15 + 0x10) = lVar8 + 0x6308e3be1d7e78d0;
      uVar19 = FUN_18043ab50(puVar16[5] + 0xf54d97a6 ^ uVar23);
      *(ulonglong *)(piVar15 + 0xc) = uVar19 ^ 0x6a690e5722724657;
      piVar15[0xe] = puVar16[7] + 0xfeccc2cd ^ uVar23 ^ 0x4fbc7cff;
      piVar15[10] = puVar16[3] ^ 0x7b3f167f ^ uVar23 ^ 0x6b612990;
      piVar15[6] = puVar16[8] + 0xa48472e0 ^ uVar23 ^ 0x39fd8dcc;
      piVar15[8] = puVar16[4] ^ 0x2b15fec1 ^ uVar23 ^ 0x2779c1dd;
      piVar15[7] = puVar16[2] ^ 0x38bb4148 ^ uVar23 ^ 0x448ae27e;
      piVar15[0x12] = *puVar16 ^ 0x348873dc ^ uVar23 ^ 0x41e927b0;
      piVar15[9] = (puVar16[6] + 0x8f726a05 ^ uVar23) + 0x28f01ff2;
      *(undefined8 *)(piVar15 + 0x13) = *(undefined8 *)(puVar16 + 9);
      FUN_1804491a0(piVar15);
      uVar19 = (ulonglong)(iVar4 + 1U);
      local_res8 = local_res8 + 0x60;
    } while ((int)(iVar4 + 1U) < DAT_1899dbc08);
  }
  FUN_180440660();
  local_2b8 = (undefined8 *)0x0;
  puStack_2b0 = (undefined8 *)0x0;
  local_2a8 = (undefined8 *)0x0;
  lVar6 = (int)(DAT_188198e08 ^ 0x2b849db3) + DAT_1899dbaf8;
  iVar5 = 0;
  puVar9 = (undefined8 *)0x0;
  if (0 < DAT_1899dbc18) {
    local_res18 = 0;
    iVar4 = DAT_1899dbc18;
    do {
      uVar19 = *(ulonglong *)(local_res18 + 8 + DAT_1899dbc20) ^ 0x56ead61b43cc4f04;
      local_res10 = 0;
      local_258 = *(uint *)(uVar19 + 0x1c) ^ 0x53c69178;
      if (local_258 != 0) {
        do {
          uVar21 = (*(uint *)(uVar19 + 0x14) ^ 0x1d3b2899) + (int)local_res10;
          lVar8 = (((ulonglong)uVar21 * 0x1f17946ef935 + 0xafd81baecafdac6 >> 0x15) + 0x54760499) *
                  0x1125f1b6;
          lVar24 = (ulonglong)uVar21 * 0x5c + lVar6;
          uVar18 = 0;
          sVar25 = (short)lVar8;
          if ((short)(*(short *)(lVar24 + 0x48) + 0x1950) != sVar25) {
            do {
              iVar4 = (int)lVar8;
              uVar22 = (ulonglong)(((*(int *)(lVar24 + 0x14) + -0x2822b502) - iVar4) + (uint)uVar18)
              ;
              iStack_298 = ((*(int *)(lVar24 + 0x14) + -0x2822b502) - iVar4) + (uint)uVar18;
              uVar21 = (*(int *)(uVar22 * 0x20 + 0x14 + (DAT_188198e58 + -0x17a3b99) + DAT_1899dbaf8
                                ) + 0xbd6fc398U ^
                       (uint)(((uVar22 * 0xb069 ^ 0x3e382f2d) * 0x24147491 >> 10 ^ 0x3e65ed2a) *
                              0x3857aaca >> 0xe)) & 0xffffff;
              if (uVar21 == 0) {
                local_2a0 = 0;
              }
              else {
                local_2a0 = *(ulonglong *)
                             (*(longlong *)(*(longlong *)(uVar19 + 0x30) + -0x15efe0164a2ec173) +
                             (ulonglong)(uVar21 - 1) * 8);
                if (local_2a0 != 0) {
                  if ((&local_2a0 < puVar9) && (local_2b8 <= &local_2a0)) {
                    uVar22 = (longlong)&local_2a0 - (longlong)local_2b8;
                    if (puVar9 == local_2a8) {
                      FUN_180450eb0(&local_2b8,1);
                      puVar9 = puStack_2b0;
                    }
                    puVar14 = (undefined4 *)((uVar22 & 0xfffffffffffffff0) + (longlong)local_2b8);
                    puVar10 = (undefined8 *)0x0;
                    if (puVar9 != (undefined8 *)0x0) {
                      uVar26 = puVar14[1];
                      uVar27 = puVar14[2];
                      uVar28 = puVar14[3];
                      *(undefined4 *)puVar9 = *puVar14;
                      *(undefined4 *)((longlong)puVar9 + 4) = uVar26;
                      *(undefined4 *)(puVar9 + 1) = uVar27;
                      *(undefined4 *)((longlong)puVar9 + 0xc) = uVar28;
                      puVar10 = puStack_2b0;
                    }
                  }
                  else {
                    if (puVar9 == local_2a8) {
                      FUN_180450eb0(&local_2b8,1);
                      puVar9 = puStack_2b0;
                    }
                    puVar10 = (undefined8 *)0x0;
                    if (puVar9 != (undefined8 *)0x0) {
                      *(undefined4 *)puVar9 = (undefined4)local_2a0;
                      *(undefined4 *)((longlong)puVar9 + 4) = local_2a0._4_4_;
                      *(int *)(puVar9 + 1) = iStack_298;
                      *(undefined4 *)((longlong)puVar9 + 0xc) = uStack_294;
                      puVar10 = puStack_2b0;
                    }
                  }
                  puVar9 = puVar10 + 2;
                  puStack_2b0 = puVar9;
                }
              }
              uVar18 = uVar18 + 1;
            } while (uVar18 < (ushort)((*(short *)(lVar24 + 0x48) + 0x1950) - sVar25));
          }
          local_res10 = local_res10 + 1;
          iVar4 = DAT_1899dbc18;
        } while (local_res10 < (*(uint *)(uVar19 + 0x1c) ^ 0x53c69178));
      }
      iVar5 = iVar5 + 1;
      local_res18 = local_res18 + 0x60;
    } while (iVar5 < iVar4);
  }
  uVar19 = uVar13;
  if (0 < (int)(DAT_1881a3630 ^ 0x421dd17c)) {
    do {
      iStack_298 = *(int *)(PTR_DAT_1881a3620 +
                           (longlong)*(int *)(PTR_DAT_1881a3608 + uVar13) * 0xc + 8);
      local_2a0 = *(ulonglong *)
                   (PTR_DAT_188139740 + (longlong)*(int *)(PTR_DAT_1881a3608 + uVar13 + 8) * 8);
      if ((&local_2a0 < puVar9) && (local_2b8 <= &local_2a0)) {
        uVar22 = (longlong)&local_2a0 - (longlong)local_2b8;
        if (puVar9 == local_2a8) {
          FUN_180450eb0(&local_2b8,1);
          puVar9 = puStack_2b0;
        }
        puVar14 = (undefined4 *)((uVar22 & 0xfffffffffffffff0) + (longlong)local_2b8);
        puVar10 = (undefined8 *)0x0;
        if (puVar9 != (undefined8 *)0x0) {
          uVar26 = *puVar14;
          uVar27 = puVar14[1];
          iVar5 = puVar14[2];
          uVar28 = puVar14[3];
LAB_18043f927:
          *(undefined4 *)puVar9 = uVar26;
          *(undefined4 *)((longlong)puVar9 + 4) = uVar27;
          *(int *)(puVar9 + 1) = iVar5;
          *(undefined4 *)((longlong)puVar9 + 0xc) = uVar28;
          puVar10 = puStack_2b0;
        }
      }
      else {
        if (puVar9 == local_2a8) {
          FUN_180450eb0(&local_2b8,1);
          puVar9 = puStack_2b0;
        }
        puVar10 = (undefined8 *)0x0;
        if (puVar9 != (undefined8 *)0x0) {
          uVar26 = (undefined4)local_2a0;
          uVar27 = local_2a0._4_4_;
          iVar5 = iStack_298;
          uVar28 = uStack_294;
          goto LAB_18043f927;
        }
      }
      puVar9 = puVar10 + 2;
      uVar21 = (int)uVar19 + 1;
      uVar13 = uVar13 + 0x10;
      uVar19 = (ulonglong)uVar21;
      puStack_2b0 = puVar9;
    } while ((int)uVar21 < (int)(DAT_1881a3630 ^ 0x421dd17c));
  }
  FUN_1804fdc10(&local_2b8);
  if (local_2b8 != (undefined8 *)0x0) {
    FUN_1804527e0(&local_2b8,local_2b8,(longlong)local_2a8 - (longlong)local_2b8 >> 4);
  }
  return 1;
}



