// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x18042D650 ================= */
/* name   = FUN_18042d650 */
/* entry  = 18042d650 */
/* body   = 528 bytes */
/* sig    = undefined FUN_18042d650() */


undefined8 FUN_18042d650(int *param_1,char *param_2,char *param_3)

{
  char cVar1;
  longlong lVar2;
  void *pvVar3;
  ulonglong uVar4;
  ulonglong uVar5;
  int iVar6;
  ulonglong uVar7;
  uint uVar8;
  char *pcVar9;
  ulonglong uVar10;
  undefined8 uVar11;
  char *local_50;
  char *local_48;
  longlong local_40;
  longlong local_38;
  
  uVar11 = 0xfffffffffffffffe;
  if (*(longlong *)(param_1 + 2) == 0) {
    FUN_1803f4990(&DAT_1899db840);
    if (*(longlong *)(param_1 + 2) == 0) {
      pvVar3 = operator_new(0x60);
      uVar10 = 0;
      uVar4 = uVar10;
      if (pvVar3 != (void *)0x0) {
        uVar4 = FUN_180428f80(pvVar3);
      }
      *(ulonglong *)(param_1 + 2) = uVar4;
      uVar4 = uVar10;
      if (param_1[7] != 0x53c69178) {
        do {
          FUN_18042bd50(param_1,(param_1[5] ^ 0x1d3b2899U) + (int)uVar4);
          uVar8 = (int)uVar4 + 1;
          uVar4 = (ulonglong)uVar8;
        } while (uVar8 < (param_1[7] ^ 0x53c69178U));
      }
      if (param_1[6] != 0x61a2155e) {
        do {
          iVar6 = *param_1 + -0x188fa8da + (int)uVar10;
          if ((iVar6 != -1) &&
             (*(int *)((DAT_188198e68 + -0x1408dbf1) + DAT_1899dbaf8 + (longlong)iVar6 * 4) != -1))
          {
            FUN_18042bd50(param_1);
          }
          uVar8 = (int)uVar10 + 1;
          uVar10 = (ulonglong)uVar8;
        } while (uVar8 < (param_1[6] ^ 0x61a2155eU));
      }
    }
    FUN_1803f72c0(&DAT_1899db840);
  }
  lVar2 = *(longlong *)(param_1 + 2);
  uVar7 = 0x1505;
  uVar4 = 0x1505;
  uVar10 = 0x1505;
  cVar1 = *param_3;
  pcVar9 = param_3;
  while (cVar1 != '\0') {
    uVar4 = uVar4 * 0x21 ^ (longlong)cVar1;
    if (pcVar9[1] == '\0') break;
    uVar10 = uVar10 * 0x21 ^ (longlong)pcVar9[1];
    pcVar9 = pcVar9 + 2;
    cVar1 = *pcVar9;
  }
  uVar5 = 0x1505;
  cVar1 = *param_2;
  pcVar9 = param_2;
  while (cVar1 != '\0') {
    uVar7 = uVar7 * 0x21 ^ (longlong)cVar1;
    if (pcVar9[1] == '\0') break;
    uVar5 = uVar5 * 0x21 ^ (longlong)pcVar9[1];
    pcVar9 = pcVar9 + 2;
    cVar1 = *pcVar9;
  }
  local_50 = param_2;
  local_48 = param_3;
  FUN_18041c670(lVar2,&local_40,&local_50,
                uVar7 * 0x1cfaa2db + (uVar5 * 0x1cfaa2db + uVar10) * 0x5d588b65 + uVar4,uVar11);
  if (((local_40 - *(longlong *)(lVar2 + 0x10) & 0xffffffffffffffe0U) + *(longlong *)(lVar2 + 0x10)
       == *(longlong *)(*(longlong *)(param_1 + 2) + 0x18)) && (local_38 == 0)) {
    uVar11 = 0;
  }
  else {
    uVar11 = FUN_18043b320(*(undefined4 *)(local_38 + 0x10));
  }
  return uVar11;
}



/* ================= 0x18042B6C0 ================= */
/* name   = FUN_18042b6c0 */
/* entry  = 18042b6c0 */
/* body   = 576 bytes */
/* sig    = undefined FUN_18042b6c0() */


void FUN_18042b6c0(undefined8 param_1,undefined8 param_2,undefined8 param_3,longlong param_4)

{
  char cVar1;
  ulonglong uVar2;
  undefined8 uVar3;
  char *pcVar4;
  ulonglong uVar5;
  char ****ppppcVar6;
  longlong *plVar7;
  char *pcVar8;
  longlong lVar9;
  char ***local_98 [2];
  longlong local_88;
  ulonglong local_80;
  byte local_78;
  undefined7 uStack_77;
  undefined8 local_68;
  ulonglong local_60;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined4 local_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  int local_38;
  undefined8 local_30;
  undefined1 local_28 [32];
  
  local_30 = 0xfffffffffffffffe;
  if (**(char **)(param_4 + 0xa8) != '\0') {
    uVar3 = FUN_1804172e0(&local_78,param_3,&DAT_1881a2348);
    FUN_1803fabc0(local_98,uVar3,*(undefined8 *)(param_4 + 0xa8));
    if (0xf < local_60) {
      uVar2 = CONCAT71(uStack_77,local_78);
      uVar5 = uVar2;
      if (0xfff < local_60 + 1) {
        if ((local_78 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        uVar5 = *(ulonglong *)(uVar2 - 8);
        if (uVar2 <= uVar5) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if (uVar2 - uVar5 < 8) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if (0x27 < uVar2 - uVar5) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
      }
      thunk_FUN_18050a3b8(uVar5);
    }
    local_60 = 0xf;
    plVar7 = (longlong *)0x0;
    local_68 = 0;
    local_78 = 0;
    pcVar4 = (char *)_calloc_base(local_88 + 1,1);
    ppppcVar6 = local_98;
    pcVar8 = pcVar4;
    if (0xf < local_80) {
      ppppcVar6 = (char ****)local_98[0];
    }
    do {
      cVar1 = *(char *)ppppcVar6;
      *pcVar8 = cVar1;
      ppppcVar6 = (char ****)((longlong)ppppcVar6 + 1);
      pcVar8 = pcVar8 + 1;
    } while (cVar1 != '\0');
    lVar9 = *(longlong *)(param_4 + 0xd0) - ((int)(DAT_188198e08 ^ 0x2b849db3) + DAT_1899dbaf8);
    lVar9 = SUB168(SEXT816(-0x4de9bd37a6f4de9b) * SEXT816(lVar9),8) + lVar9;
    local_38 = (int)(lVar9 >> 6) - (int)(lVar9 >> 0x3f);
    local_58._0_4_ = (undefined4)param_2;
    local_58._4_4_ = (undefined4)((ulonglong)param_2 >> 0x20);
    uStack_50._0_4_ = SUB84(pcVar4,0);
    uStack_50._4_4_ = (undefined4)((ulonglong)pcVar4 >> 0x20);
    local_48 = (undefined4)local_58;
    uStack_44 = local_58._4_4_;
    uStack_40 = (undefined4)uStack_50;
    uStack_3c = uStack_50._4_4_;
    local_58 = param_2;
    uStack_50 = pcVar4;
    FUN_1804201e0(param_1,local_28,&local_48,&local_48);
    while (*(longlong *)(param_4 + 0xc0) == 0) {
      if (plVar7 == (longlong *)0x0) {
        FUN_18044c7a0(param_4);
        if (*(short *)(param_4 + 0x122) == 0) break;
        plVar7 = *(longlong **)(param_4 + 0x78);
      }
      else {
        plVar7 = plVar7 + 1;
        if ((longlong *)
            (*(longlong *)(param_4 + 0x78) + (ulonglong)*(ushort *)(param_4 + 0x122) * 8) <= plVar7)
        break;
      }
      if (*plVar7 == 0) break;
      FUN_18042b6c0(param_1,param_2,local_98);
    }
    if (0xf < local_80) {
      ppppcVar6 = (char ****)local_98[0];
      if (0xfff < local_80 + 1) {
        if (((ulonglong)local_98[0] & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        ppppcVar6 = (char ****)local_98[0][-1];
        if (local_98[0] <= ppppcVar6) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if ((ulonglong)((longlong)local_98[0] - (longlong)ppppcVar6) < 8) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if (0x27 < (ulonglong)((longlong)local_98[0] - (longlong)ppppcVar6)) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
      }
      thunk_FUN_18050a3b8(ppppcVar6);
    }
  }
  return;
}



/* ================= 0x1804201E0 ================= */
/* name   = FUN_1804201e0 */
/* entry  = 1804201e0 */
/* body   = 507 bytes */
/* sig    = undefined FUN_1804201e0() */


longlong * FUN_1804201e0(longlong param_1,longlong *param_2,undefined8 *param_3,undefined8 param_4)

{
  char cVar1;
  char cVar2;
  bool bVar3;
  byte bVar4;
  undefined8 uVar5;
  ulonglong uVar6;
  ulonglong uVar7;
  char *pcVar8;
  ulonglong uVar9;
  sbyte sVar10;
  longlong lVar11;
  ulonglong uVar12;
  longlong *plVar13;
  ulonglong uVar14;
  sbyte local_res8;
  longlong lStack_60;
  undefined7 uStack_47;
  
  if (*(ulonglong *)(param_1 + 0x38) < *(ulonglong *)(param_1 + 0x48)) {
    if (*(ulonglong *)(param_1 + 0x38) + *(longlong *)(param_1 + 0x40) <
        *(ulonglong *)(param_1 + 0x50)) goto LAB_180420235;
    uVar5 = *(undefined8 *)(param_1 + 0x30);
  }
  else {
    uVar5 = FUN_180415a40(param_1 + 8);
  }
  FUN_1804230d0(param_1,uVar5);
LAB_180420235:
  bVar3 = false;
  local_res8 = 0;
  uVar12 = 0;
  uVar6 = FUN_18042aad0(param_1 + 1,param_3);
  uVar14 = uVar12;
  do {
    uVar6 = uVar6 & *(ulonglong *)(param_1 + 8);
    uVar9 = uVar6 >> 6;
    sVar10 = (sbyte)(uVar6 & 0x3f);
    plVar13 = (longlong *)(*(longlong *)(param_1 + 0x28) + uVar9 * 0x20);
    uVar7 = 1L << sVar10;
    if ((plVar13[1] & uVar7) == 0) {
      if (((plVar13[2] & uVar7) == 0) || (*(ulonglong *)(param_1 + 0x30) <= uVar14)) {
        if (bVar3) {
          lVar11 = FUN_180425570(*(longlong *)(param_1 + 0x28) + uVar12 * 0x20,param_1,local_res8,
                                 param_4);
          *(longlong *)(param_1 + 0x38) = *(longlong *)(param_1 + 0x38) + 1;
          *(longlong *)(param_1 + 0x40) = *(longlong *)(param_1 + 0x40) + -1;
          *param_2 = *(longlong *)(param_1 + 0x10) + uVar12 * 0x20;
          param_2[1] = lVar11;
          param_2[2] = CONCAT71(uStack_47,1);
          return param_2;
        }
        lStack_60 = FUN_180425570(*(longlong *)(param_1 + 0x28) + uVar9 * 0x20,param_1,uVar6 & 0x3f,
                                  param_4);
        *(longlong *)(param_1 + 0x38) = *(longlong *)(param_1 + 0x38) + 1;
        *(undefined1 *)(param_2 + 2) = 1;
        goto LAB_1804203a9;
      }
      if (!bVar3) {
        bVar3 = true;
        uVar12 = uVar9;
        local_res8 = sVar10;
      }
    }
    else {
      bVar4 = FUN_180415ac0(uVar7 - 1 & plVar13[1]);
      lStack_60 = *plVar13 + (ulonglong)bVar4 * 0x18;
      pcVar8 = (char *)*param_3;
      lVar11 = *(longlong *)(*plVar13 + (ulonglong)bVar4 * 0x18) - (longlong)pcVar8;
      do {
        cVar1 = *pcVar8;
        cVar2 = pcVar8[lVar11];
        if (cVar1 != cVar2) break;
        pcVar8 = pcVar8 + 1;
      } while (cVar2 != '\0');
      if (cVar1 == cVar2) {
        pcVar8 = (char *)param_3[1];
        lVar11 = *(longlong *)(lStack_60 + 8) - (longlong)pcVar8;
        do {
          cVar1 = *pcVar8;
          cVar2 = pcVar8[lVar11];
          if (cVar1 != cVar2) break;
          pcVar8 = pcVar8 + 1;
        } while (cVar2 != '\0');
        if (cVar1 == cVar2) {
          *(undefined1 *)(param_2 + 2) = 0;
LAB_1804203a9:
          *param_2 = uVar9 * 0x20 + *(longlong *)(param_1 + 0x10);
          param_2[1] = lStack_60;
          return param_2;
        }
      }
    }
    uVar14 = uVar14 + 1;
    uVar6 = uVar6 + uVar14;
  } while( true );
}



/* ================= 0x18043E870 ================= */
/* name   = FUN_18043e870 */
/* entry  = 18043e870 */
/* body   = 450 bytes */
/* sig    = undefined FUN_18043e870() */


void FUN_18043e870(int *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  longlong lVar5;
  undefined8 local_28;
  undefined8 uStack_20;
  undefined8 local_18;
  undefined8 uStack_10;
  
  uVar3 = 0;
  uVar4 = uVar3;
  if (param_1[7] != 0x53c69178) {
    do {
      uVar1 = (param_1[5] ^ 0x1d3b2899U) + uVar4;
      if (uVar1 == 0xffffffff) {
        local_28 = 0;
        uStack_20 = 0;
      }
      else {
        local_28 = (((ulonglong)uVar1 * 0x1f17946ef935 + 0xafd81baecafdac6 >> 0x15) + 0x54760499) *
                   0x1125f1b6;
        uStack_20 = (ulonglong)uVar1 * 0x5c +
                    ((longlong)DAT_188198e08 ^ 0x2b849db3U) + DAT_1899dbaf8;
      }
      local_18._0_4_ = (int)local_28;
      if (*(int *)(uStack_20 + 4) - (int)local_18 != 0xfbe4139) {
        return;
      }
      local_18._4_4_ = local_28._4_4_;
      uStack_10._0_4_ = (undefined4)uStack_20;
      uStack_10._4_4_ = uStack_20._4_4_;
      FUN_18042b910(param_1,&local_18);
      uVar4 = uVar4 + 1;
    } while (uVar4 < (param_1[7] ^ 0x53c69178U));
  }
  lVar5 = DAT_1899dbaf8;
  if (param_1[6] != 0x61a2155e) {
    do {
      iVar2 = *param_1 + -0x188fa8da + uVar3;
      if (iVar2 != -1) {
        uVar4 = *(uint *)((DAT_188198e68 + -0x1408dbf1) + lVar5 + (longlong)iVar2 * 4);
        if (uVar4 != 0xffffffff) {
          local_18 = (((ulonglong)uVar4 * 0x1f17946ef935 + 0xafd81baecafdac6 >> 0x15) + 0x54760499)
                     * 0x1125f1b6;
          uStack_10 = (ulonglong)uVar4 * 0x5c + ((longlong)DAT_188198e08 ^ 0x2b849db3U) + lVar5;
          if (*(int *)(uStack_10 + 4) - (int)local_18 != 0xfbe4139) {
            return;
          }
          FUN_18042b910(param_1,&local_18);
          lVar5 = DAT_1899dbaf8;
        }
      }
      uVar3 = uVar3 + 1;
    } while (uVar3 < (param_1[6] ^ 0x61a2155eU));
  }
  return;
}



