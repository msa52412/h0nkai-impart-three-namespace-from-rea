// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x180443FC0 ================= */
/* name   = FUN_180443fc0 */
/* entry  = 180443fc0 */
/* body   = 526 bytes */
/* sig    = undefined FUN_180443fc0() */


undefined8 FUN_180443fc0(void)

{
  ulonglong uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  ulonglong uVar4;
  byte *pbVar5;
  int local_res8 [2];
  undefined8 uVar6;
  char *local_80;
  undefined8 local_78;
  byte local_70;
  undefined7 uStack_6f;
  undefined8 local_60;
  ulonglong local_58;
  byte local_50;
  undefined7 uStack_4f;
  undefined8 local_40;
  ulonglong local_38;
  ulonglong local_30 [3];
  ulonglong local_18;
  
  uVar6 = 0xfffffffffffffffe;
  uVar2 = FUN_1804f1140(&local_50);
  local_80 = "Metadata";
  local_78 = 8;
  FUN_1803fd190(local_30,uVar2,&local_80);
  if (0xf < local_38) {
    uVar1 = CONCAT71(uStack_4f,local_50);
    uVar4 = uVar1;
    if (0xfff < local_38 + 1) {
      if ((local_50 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      uVar4 = *(ulonglong *)(uVar1 - 8);
      if (uVar1 <= uVar4) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      if (uVar1 - uVar4 < 8) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      if (0x27 < uVar1 - uVar4) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
    }
    thunk_FUN_18050a3b8(uVar4);
  }
  local_38 = 0xf;
  uVar3 = 0;
  local_40 = 0;
  local_50 = 0;
  local_80 = "global-metadata.dat";
  local_78 = 0x13;
  FUN_1803fd190(&local_70,local_30,&local_80);
  local_res8[0] = 0;
  uVar2 = FUN_1803f4cc0(&local_70,3,1,1,0,local_res8,uVar6);
  if (local_res8[0] == 0) {
    uVar3 = FUN_1804f1b20(uVar2);
    FUN_1803f0dd0(uVar2,local_res8);
  }
  else {
    pbVar5 = &local_70;
    if (0xf < local_58) {
      pbVar5 = (byte *)CONCAT71(uStack_6f,local_70);
    }
    FUN_1804f34f0("ERROR: Could not open %s",pbVar5);
  }
  if (0xf < local_58) {
    uVar1 = CONCAT71(uStack_6f,local_70);
    uVar4 = uVar1;
    if (0xfff < local_58 + 1) {
      if ((local_70 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      uVar4 = *(ulonglong *)(uVar1 - 8);
      if (uVar1 <= uVar4) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      if (uVar1 - uVar4 < 8) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      if (0x27 < uVar1 - uVar4) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
    }
    thunk_FUN_18050a3b8(uVar4);
  }
  local_58 = 0xf;
  local_60 = 0;
  local_70 = 0;
  if (0xf < local_18) {
    uVar4 = local_30[0];
    if (0xfff < local_18 + 1) {
      if ((local_30[0] & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      uVar4 = *(ulonglong *)(local_30[0] - 8);
      if (local_30[0] <= uVar4) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      if (local_30[0] - uVar4 < 8) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
      if (0x27 < local_30[0] - uVar4) {
                    /* WARNING: Subroutine does not return */
        FUN_180509dc8();
      }
    }
    thunk_FUN_18050a3b8(uVar4);
  }
  return uVar3;
}



/* ================= 0x180440079 ================= */
/* name   = FUN_180440070 */
/* entry  = 180440070 */
/* body   = 163 bytes */
/* sig    = undefined FUN_180440070() */


void FUN_180440070(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined8 local_20;
  undefined8 local_18;
  undefined8 local_10;
  
  FUN_1804fb780(PTR_DAT_1881a61b8,(longlong)(DAT_1881a61d0 + -0x2304c9ab) << 3,param_3,param_4,
                0xfffffffffffffffe);
  FUN_180440120();
  FUN_1804409f0();
  FUN_180440220();
  if (DAT_1881396a7 != '\0') {
    local_20 = 0;
    local_18 = 0;
    local_10 = 0;
    FUN_180440c10(0,(ulonglong)(longlong)(int)(DAT_188198e38 ^ 0x58bb89eb) >> 3,&local_20,0);
    thunk_FUN_18050a3d4(0);
  }
  if (DAT_1881a61b4 != 0x66c2e601) {
    FUN_180440500(DAT_1881a61b4 + -0x66c2e602);
    return;
  }
  return;
}



/* ================= 0x18043EC20 ================= */
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



/* ================= 0x18041C210 ================= */
/* name   = FUN_18041c210 */
/* entry  = 18041c210 */
/* body   = 208 bytes */
/* sig    = undefined FUN_18041c210() */


longlong * FUN_18041c210(longlong param_1,longlong *param_2,int *param_3,ulonglong param_4)

{
  longlong lVar1;
  byte bVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  longlong *plVar5;
  
  param_4 = param_4 & *(ulonglong *)(param_1 + 8);
  uVar4 = 0;
  do {
    plVar5 = (longlong *)((param_4 >> 6) * 0x20 + *(longlong *)(param_1 + 0x28));
    uVar3 = 1L << ((byte)param_4 & 0x3f);
    if ((plVar5[1] & uVar3) == 0) {
      if (((plVar5[2] & uVar3) == 0) || (*(ulonglong *)(param_1 + 0x30) <= uVar4)) {
        *param_2 = *(longlong *)(param_1 + 0x18);
        param_2[1] = 0;
        return param_2;
      }
    }
    else {
      bVar2 = FUN_180415ac0(uVar3 - 1 & plVar5[1]);
      lVar1 = *plVar5;
      if (*param_3 == *(int *)(lVar1 + (ulonglong)bVar2 * 8)) {
        *param_2 = (param_4 >> 6) * 0x20 + *(longlong *)(param_1 + 0x10);
        param_2[1] = lVar1 + (ulonglong)bVar2 * 8;
        return param_2;
      }
    }
    uVar4 = uVar4 + 1;
    param_4 = param_4 + uVar4 & *(ulonglong *)(param_1 + 8);
  } while( true );
}



/* ================= 0x1804F1B20 ================= */
/* name   = FUN_1804f1b20 */
/* entry  = 1804f1b20 */
/* body   = 171 bytes */
/* sig    = undefined FUN_1804f1b20() */


undefined8 FUN_1804f1b20(undefined8 param_1)

{
  int iVar1;
  int iVar2;
  undefined8 uVar3;
  int local_res10 [2];
  
  local_res10[0] = 0;
  iVar1 = FUN_1803f3790(param_1,local_res10);
  if (local_res10[0] != 0) {
    FUN_1804f4180("########MemoryMappedFile::ReadToMemoryDirect File::GetLength Failed########\n");
    return 0;
  }
  uVar3 = (*(code *)PTR__malloc_base_18993c868)((longlong)iVar1);
  iVar2 = FUN_1803f53c0(param_1,uVar3,iVar1,local_res10);
  if ((iVar2 == iVar1) && (local_res10[0] == 0)) {
    return uVar3;
  }
  (*(code *)PTR_FUN_18993c878)(uVar3);
  FUN_1804f4180("########MemoryMappedFile::ReadToMemoryDirect File::Read Failed########\n");
  return 0;
}



/* ================= 0x1804ED510 ================= */
/* name   = FUN_1804ed510 */
/* entry  = 1804ed510 */
/* body   = 7 bytes */
/* sig    = undefined FUN_1804ed510() */


void FUN_1804ed510(undefined4 param_1)

{
  DAT_1899de1c8 = param_1;
  return;
}



/* ================= 0x1804F09A0 ================= */
/* name   = FUN_1804f09a0 */
/* entry  = 1804f09a0 */
/* body   = 135 bytes */
/* sig    = undefined FUN_1804f09a0() */


longlong FUN_1804f09a0(longlong param_1,longlong param_2,longlong param_3)

{
  longlong lVar1;
  longlong lVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  ulonglong uVar5;
  
  lVar1 = *(longlong *)(param_1 + 0x10);
  uVar3 = *(longlong *)(param_1 + 8) - lVar1;
  uVar5 = param_2 * param_3 + 7U & 0xfffffffffffffff8;
  if (uVar3 < uVar5) {
    lVar2 = *(longlong *)(param_1 + 0x18);
    uVar4 = (lVar2 - uVar3) + -1 + uVar5 & ~(lVar2 - 1U);
    uVar3 = lVar2 * 4;
    if ((ulonglong)(lVar2 * 4) < uVar4) {
      uVar3 = uVar4;
    }
    FUN_1804f13e0(param_1,uVar3);
  }
  *(longlong *)(param_1 + 0x10) = *(longlong *)(param_1 + 0x10) + uVar5;
  FUN_180500080(lVar1,0,uVar5);
  return lVar1;
}



/* ================= 0x1803F4CC0 ================= */
/* name   = FUN_1803f4cc0 */
/* entry  = 1803f4cc0 */
/* body   = 95 bytes */
/* sig    = undefined FUN_1803f4cc0() */


void FUN_1803f4cc0(undefined8 *param_1,int param_2)

{
  undefined1 local_30 [40];
  
  if (0xf < (ulonglong)param_1[3]) {
    param_1 = (undefined8 *)*param_1;
  }
  FUN_1804f3400(local_30,param_1);
                    /* WARNING: Could not recover jumptable at 0x0001803f4d1d. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)((ulonglong)*(uint *)(&DAT_1803f4e50 + (longlong)(param_2 + -1) * 4) + 0x180000000))();
  return;
}



/* ================= 0x1803F0DD0 ================= */
/* name   = FUN_1803f0dd0 */
/* entry  = 1803f0dd0 */
/* body   = 49 bytes */
/* sig    = undefined FUN_1803f0dd0() */


undefined4 FUN_1803f0dd0(HANDLE param_1,DWORD *param_2)

{
  BOOL BVar1;
  DWORD DVar2;
  
  *param_2 = 0;
  BVar1 = CloseHandle(param_1);
  if (BVar1 != 0) {
    return 1;
  }
  DVar2 = GetLastError();
  *param_2 = DVar2;
  return 0;
}



/* ================= 0x18043D3D4 ================= */
/* name   = FUN_18043d350 */
/* entry  = 18043d350 */
/* body   = 4444 bytes */
/* sig    = undefined FUN_18043d350() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_18043d350(undefined8 param_1)

{
  ulonglong uVar1;
  char cVar2;
  int iVar3;
  longlong lVar4;
  undefined8 uVar5;
  longlong lVar6;
  undefined8 *puVar7;
  ulonglong uVar8;
  byte *local_res10;
  undefined *local_res18;
  byte local_90;
  undefined7 uStack_8f;
  undefined8 local_80;
  ulonglong local_78;
  byte local_70;
  undefined7 uStack_6f;
  undefined8 local_60;
  ulonglong local_58;
  byte local_50;
  undefined7 uStack_4f;
  undefined8 local_40;
  ulonglong local_38;
  
  local_res18 = &DAT_1899db980;
  FUN_1803f4990(&DAT_1899db980);
  if (DAT_1899dbacc < 1) {
    DAT_1899dbacc = DAT_1899dbacc + 1;
    _guard_check_icall();
    FUN_1803f4430();
    FUN_18043eb80();
    DAT_1899dbc80 = &DAT_1881a295c;
    thunk_FUN_1803f4450();
    FUN_1803f4320();
    FUN_1804f0a30();
    cVar2 = FUN_18043ec20();
    if (cVar2 == '\0') {
      DAT_1899dbacc = DAT_1899dbacc + -1;
      uVar5 = 0;
    }
    else {
      FUN_1804fb480();
      FUN_1803f6950(FUN_1804562f0);
      local_res10 = operator_new(0x18);
      DAT_1899dbb60 = (byte *)0x0;
      if (local_res10 != (byte *)0x0) {
        local_res10[0] = 0;
        local_res10[1] = 0;
        local_res10[2] = 0;
        local_res10[3] = 0;
        local_res10[4] = 0;
        local_res10[5] = 0;
        local_res10[6] = 0;
        local_res10[7] = 0;
        local_res10[8] = 0;
        local_res10[9] = 0;
        local_res10[10] = 0;
        local_res10[0xb] = 0;
        local_res10[0xc] = 0;
        local_res10[0xd] = 0;
        local_res10[0xe] = 0;
        local_res10[0xf] = 0;
        local_res10[0x10] = 0;
        local_res10[0x11] = 0;
        local_res10[0x12] = 0;
        local_res10[0x13] = 0;
        local_res10[0x14] = 0;
        local_res10[0x15] = 0;
        local_res10[0x16] = 0;
        local_res10[0x17] = 0;
        DAT_1899dbb60 = local_res10;
      }
      FUN_18043f9a0();
      FUN_1803faa70(_malloc_base);
      FUN_180500080(&DAT_1899db1c0,0,0x318);
      lVar4 = FUN_180443d20("mscorlib.dll");
      DAT_1899db1c0 = *(ulonglong *)(lVar4 + 8) ^ 0x56ead61b43cc4f04;
      DAT_1899db1c8 = FUN_18042d650(DAT_1899db1c0,"System","Object");
      DAT_1899db1d8 = FUN_18042d650(DAT_1899db1c0,"System",&DAT_1881a2970);
      DAT_1899db1e0 = FUN_18042d650(DAT_1899db1c0,"System","Boolean");
      DAT_1899db1d0 = FUN_18042d650(DAT_1899db1c0,"System",&DAT_1881a2980);
      DAT_1899db1e8 = FUN_18042d650(DAT_1899db1c0,"System","SByte");
      DAT_1899db1f0 = FUN_18042d650(DAT_1899db1c0,"System","Int16");
      DAT_1899db1f8 = FUN_18042d650(DAT_1899db1c0,"System","UInt16");
      DAT_1899db200 = FUN_18042d650(DAT_1899db1c0,"System","Int32");
      DAT_1899db208 = FUN_18042d650(DAT_1899db1c0,"System","UInt32");
      DAT_1899db218 = FUN_18042d650(DAT_1899db1c0,"System","UIntPtr");
      DAT_1899db210 = FUN_18042d650(DAT_1899db1c0,"System","IntPtr");
      DAT_1899db220 = FUN_18042d650(DAT_1899db1c0,"System","Int64");
      DAT_1899db228 = FUN_18042d650(DAT_1899db1c0,"System","UInt64");
      DAT_1899db230 = FUN_18042d650(DAT_1899db1c0,"System","Single");
      DAT_1899db238 = FUN_18042d650(DAT_1899db1c0,"System","Double");
      DAT_1899db240 = FUN_18042d650(DAT_1899db1c0,"System",&DAT_1881a29e0);
      DAT_1899db248 = FUN_18042d650(DAT_1899db1c0,"System","String");
      DAT_1899db250 = FUN_18042d650(DAT_1899db1c0,"System",&DAT_1881a29f0);
      DAT_1899db258 = FUN_18042d650(DAT_1899db1c0,"System","Array");
      DAT_1899db260 = FUN_18042d650(DAT_1899db1c0,"System","Delegate");
      DAT_1899db268 = FUN_18042d650(DAT_1899db1c0,"System","MulticastDelegate");
      DAT_1899db270 = FUN_18042d650(DAT_1899db1c0,"System.Runtime.Remoting.Messaging","AsyncResult")
      ;
      DAT_1899db390 = FUN_18042d650(DAT_1899db1c0,"System","MonoAsyncCall");
      DAT_1899db278 = FUN_18042d650(DAT_1899db1c0,"System.Threading","ManualResetEvent");
      DAT_1899db298 = FUN_18042d650(DAT_1899db1c0,"System",&DAT_1881a2a84);
      DAT_1899db2a0 = FUN_18042d650(DAT_1899db1c0,"System","MonoType");
      DAT_1899db2b8 = FUN_18042d650(DAT_1899db1c0,"System.Threading","Thread");
      DAT_1899db2c0 = FUN_18042d650(DAT_1899db1c0,"System.Threading","InternalThread");
      DAT_1899db358 = FUN_18042d650(DAT_1899db1c0,"System","RuntimeType");
      DAT_1899db2c8 = FUN_18042d650(DAT_1899db1c0,"System","AppDomain");
      DAT_1899db2d0 = FUN_18042d650(DAT_1899db1c0,"System","AppDomainSetup");
      DAT_1899db2d8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","FieldInfo");
      DAT_1899db2e0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MethodInfo");
      DAT_1899db2e8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","PropertyInfo");
      DAT_1899db2f0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","EventInfo");
      _DAT_1899db2f8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoEventInfo");
      _DAT_1899db300 = FUN_18042d650(DAT_1899db1c0,"System.Text","StringBuilder");
      DAT_1899db308 = FUN_18042d650(DAT_1899db1c0,"System.Diagnostics","StackFrame");
      DAT_1899db310 = FUN_18042d650(DAT_1899db1c0,"System.Diagnostics","StackTrace");
      DAT_1899db320 = FUN_18042d650(DAT_1899db1c0,"System","TypedReference");
      DAT_1899db330 = FUN_18042d650(DAT_1899db1c0,"System.Collections.Generic","IList`1");
      DAT_1899db338 = FUN_18042d650(DAT_1899db1c0,"System.Collections.Generic","ICollection`1");
      DAT_1899db340 = FUN_18042d650(DAT_1899db1c0,"System.Collections.Generic","IEnumerable`1");
      DAT_1899db348 = FUN_18042d650(DAT_1899db1c0,"System.Collections.Generic","IReadOnlyList`1");
      DAT_1899db350 =
           FUN_18042d650(DAT_1899db1c0,"System.Collections.Generic","IReadOnlyCollection`1");
      DAT_1899db360 = FUN_18042d650(DAT_1899db1c0,"System","Nullable`1");
      _DAT_1899db380 = FUN_18042d650(DAT_1899db1c0,"System","Version");
      DAT_1899db388 = FUN_18042d650(DAT_1899db1c0,"System.Globalization","CultureInfo");
      DAT_1899db398 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","Assembly");
      _DAT_1899db3a8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","AssemblyName");
      DAT_1899db3a0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoAssembly");
      _DAT_1899db3b0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoField");
      DAT_1899db3b8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoMethod");
      DAT_1899db3c0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoCMethod");
      _DAT_1899db3c8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoMethodInfo");
      _DAT_1899db3d0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoPropertyInfo");
      _DAT_1899db3d8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","ParameterInfo");
      DAT_1899db3e0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","MonoParameterInfo");
      DAT_1899db3e8 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","Module");
      _DAT_1899db3f0 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","Pointer");
      _DAT_1899db2a8 = FUN_18042d650(DAT_1899db1c0,"System","Exception");
      _DAT_1899db3f8 = FUN_18042d650(DAT_1899db1c0,"System","SystemException");
      _DAT_1899db400 = FUN_18042d650(DAT_1899db1c0,"System","ArgumentException");
      _DAT_1899db328 = FUN_18042d650(DAT_1899db1c0,"System","MarshalByRefObject");
      DAT_1899db368 = FUN_18042d650(DAT_1899db1c0,"System","__Il2CppComObject");
      _DAT_1899db410 = FUN_18042d650(DAT_1899db1c0,"System.Runtime.InteropServices","SafeHandle");
      _DAT_1899db418 = FUN_18042d650(DAT_1899db1c0,"System.Globalization","SortKey");
      DAT_1899db420 = FUN_18042d650(DAT_1899db1c0,"System",&DAT_1881a2cf0);
      _DAT_1899db428 = FUN_18042d650(DAT_1899db1c0,"System.Runtime.InteropServices","ErrorWrapper");
      _DAT_1899db430 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","Missing");
      DAT_1899db370 = FUN_18042d650(DAT_1899db1c0,"System","Attribute");
      DAT_1899db378 = FUN_18042d650(DAT_1899db1c0,"System.Reflection","CustomAttributeData");
      DAT_1899db438 = FUN_18042d650(DAT_1899db1c0,"System","ValueType");
      _DAT_1899db470 = FUN_18042d650(DAT_1899db1c0,"System.Collections.Generic","KeyValuePair`2");
      _DAT_1899db490 = FUN_18042d650(DAT_1899db1c0,"System",&DAT_1881a2d3c);
      DAT_1899db440 = FUN_18042d650(DAT_1899db1c0,"System.Threading","_ThreadPoolWaitCallback");
      DAT_1899db450 =
           FUN_18042d650(DAT_1899db1c0,"System.Runtime.Remoting.Messaging","MonoMethodMessage");
      DAT_1899db448 = FUN_180436f50(DAT_1899db440,"PerformWaitCallback",0,0,0);
      DAT_1899db498 = FUN_18042d650(DAT_1899db1c0,"System","SByteEnum");
      DAT_1899db4a0 = FUN_18042d650(DAT_1899db1c0,"System","Int16Enum");
      DAT_1899db4a8 = FUN_18042d650(DAT_1899db1c0,"System","Int32Enum");
      DAT_1899db4b0 = FUN_18042d650(DAT_1899db1c0,"System","Int64Enum");
      DAT_1899db4b8 = FUN_18042d650(DAT_1899db1c0,"System","ByteEnum");
      DAT_1899db4c0 = FUN_18042d650(DAT_1899db1c0,"System","UInt16Enum");
      DAT_1899db4c8 = FUN_18042d650(DAT_1899db1c0,"System","UInt32Enum");
      DAT_1899db4d0 = FUN_18042d650(DAT_1899db1c0,"System","UInt64Enum");
      FUN_18043e870(DAT_1899db1c0);
      lVar4 = FUN_180443d20("System");
      if (lVar4 != 0) {
        DAT_1899db488 =
             FUN_18042d650(*(ulonglong *)(lVar4 + 8) ^ 0x56ead61b43cc4f04,"System",&DAT_1881a2e0c);
      }
      lVar4 = FUN_180443d20("WindowsRuntimeMetadata");
      if (lVar4 != 0) {
        uVar8 = *(ulonglong *)(lVar4 + 8) ^ 0x56ead61b43cc4f04;
        _DAT_1899db458 = FUN_18042d650(uVar8,"Windows.Foundation","IReference`1");
        _DAT_1899db460 = FUN_18042d650(uVar8,"Windows.Foundation","IReferenceArray`1");
        DAT_1899db468 = FUN_18042d650(uVar8,"Windows.Foundation.Collections","IKeyValuePair`2");
        DAT_1899db468 = FUN_18042d650(uVar8,"Windows.Foundation.Collections","IKeyValuePair`2");
        DAT_1899db478 = FUN_18042d650(uVar8,"Windows.Foundation",&DAT_1881a2e0c);
        DAT_1899db480 = FUN_18042d650(uVar8,"Windows.Foundation","IUriRuntimeClass");
      }
      FUN_18043d300(DAT_1899db248);
      FUN_1803f7160();
      if (DAT_1899dbb98 == 0) {
        DAT_1899dbb98 = thunk_FUN_1804df2c0(0x30);
      }
      lVar4 = DAT_1899dbb98;
      _DAT_1899dbb88 = FUN_18042ccf0(DAT_1899dbb98);
      uVar5 = FUN_1804457f0(DAT_1899db2d0);
      lVar6 = FUN_1804457f0(DAT_1899db2c8);
      FUN_180268160(lVar6 + 0x18,lVar4);
      FUN_180268160(lVar4,lVar6);
      FUN_180268160(lVar4 + 8,uVar5);
      *(undefined4 *)(lVar4 + 0x20) = 1;
      uVar5 = FUN_180451910(param_1);
      *(undefined8 *)(lVar4 + 0x18) = uVar5;
      if (DAT_18993b6c0 == -1) {
        DAT_18993b6c0 = FUN_18042bf60(4);
      }
      FUN_1804fb520();
      uVar5 = DAT_1899db248;
      puVar7 = (undefined8 *)thunk_FUN_1804df2c0(0x1a);
      DAT_1899dbb50 = puVar7;
      *puVar7 = uVar5;
      *(undefined4 *)(puVar7 + 2) = 0;
      *(undefined2 *)((longlong)puVar7 + 0x14) = 0;
      FUN_1804405b0();
      FUN_1804ecfa0();
      FUN_180440070();
      FUN_18043ea40();
      DAT_1899db1bc = 1;
      local_38 = 0xf;
      local_40 = 0;
      local_50 = 0;
      FUN_1803f92e0(&local_50,&DAT_1881a2e54,3);
      local_78 = 0xf;
      local_80 = 0;
      local_90 = 0;
      FUN_1803f92e0(&local_90,"MONO_REFLECTION_SERIALIZER",0x1a);
      FUN_1803f66e0(&local_90,&local_50);
      if (0xf < local_78) {
        uVar1 = CONCAT71(uStack_8f,local_90);
        uVar8 = uVar1;
        if (0xfff < local_78 + 1) {
          if ((local_90 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar8 = *(ulonglong *)(uVar1 - 8);
          if (uVar1 <= uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (uVar1 - uVar8 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < uVar1 - uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar8);
      }
      local_78 = 0xf;
      local_80 = 0;
      local_90 = 0;
      if (0xf < local_38) {
        uVar1 = CONCAT71(uStack_4f,local_50);
        uVar8 = uVar1;
        if (0xfff < local_38 + 1) {
          if ((local_50 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar8 = *(ulonglong *)(uVar1 - 8);
          if (uVar1 <= uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (uVar1 - uVar8 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < uVar1 - uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar8);
      }
      local_38 = 0xf;
      local_40 = 0;
      local_50 = 0;
      FUN_1803f92e0(&local_50,&DAT_1881a2e74,2);
      local_78 = 0xf;
      local_80 = 0;
      local_90 = 0;
      FUN_1803f92e0(&local_90,"MONO_XMLSERIALIZER_THS",0x16);
      FUN_1803f66e0(&local_90,&local_50);
      if (0xf < local_78) {
        uVar1 = CONCAT71(uStack_8f,local_90);
        uVar8 = uVar1;
        if (0xfff < local_78 + 1) {
          if ((local_90 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar8 = *(ulonglong *)(uVar1 - 8);
          if (uVar1 <= uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (uVar1 - uVar8 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < uVar1 - uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar8);
      }
      local_78 = 0xf;
      local_80 = 0;
      local_90 = 0;
      if (0xf < local_38) {
        uVar1 = CONCAT71(uStack_4f,local_50);
        uVar8 = uVar1;
        if (0xfff < local_38 + 1) {
          if ((local_50 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar8 = *(ulonglong *)(uVar1 - 8);
          if (uVar1 <= uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (uVar1 - uVar8 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < uVar1 - uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar8);
      }
      uVar5 = FUN_18042d650(DAT_1899db1c0,"System.Runtime.Remoting.Contexts","Context");
      lVar6 = FUN_1804457f0(uVar5);
      *(undefined4 *)(lVar6 + 0x10) = *(undefined4 *)(lVar4 + 0x20);
      *(undefined4 *)(lVar6 + 0x14) = 0;
      FUN_180268160((undefined8 *)(lVar4 + 0x10),lVar6);
      FUN_18042e520(*(undefined8 *)(lVar4 + 0x10));
      FUN_1803f2970(&local_70);
      FUN_18044a6a0(&local_70);
      iVar3 = FUN_1804f13d0();
      if (iVar3 == 0) {
        local_res10 = &local_70;
        if (0xf < local_58) {
          local_res10 = (byte *)CONCAT71(uStack_6f,local_70);
        }
        FUN_1804f2f60(&local_res10,1);
      }
      FUN_18042f040();
      uVar5 = 1;
      if (0xf < local_58) {
        uVar1 = CONCAT71(uStack_6f,local_70);
        uVar8 = uVar1;
        if (0xfff < local_58 + 1) {
          if ((local_70 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          uVar8 = *(ulonglong *)(uVar1 - 8);
          if (uVar1 <= uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (uVar1 - uVar8 < 8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
          if (0x27 < uVar1 - uVar8) {
                    /* WARNING: Subroutine does not return */
            FUN_180509dc8();
          }
        }
        thunk_FUN_18050a3b8(uVar8);
      }
      local_58 = 0xf;
      local_60 = 0;
      local_70 = 0;
    }
  }
  else {
    uVar5 = 1;
    DAT_1899dbacc = DAT_1899dbacc + 1;
  }
  FUN_1803f72c0(&DAT_1899db980);
  return uVar5;
}



