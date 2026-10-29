// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x18042B910 ================= */
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



/* ================= 0x18042BDE0 ================= */
/* name   = FUN_18042bd50 */
/* entry  = 18042bd50 */
/* body   = 293 bytes */
/* sig    = undefined FUN_18042bd50() */


void FUN_18042bd50(longlong param_1,uint param_2)

{
  int iVar1;
  undefined8 uVar2;
  longlong lVar3;
  int iVar4;
  longlong local_48;
  longlong lStack_40;
  uint local_38;
  undefined1 local_28 [32];
  
  if (param_2 == 0xffffffff) {
    lVar3 = 0;
    local_48 = lVar3;
  }
  else {
    local_48 = (((ulonglong)param_2 * 0x1f17946ef935 + 0xafd81baecafdac6 >> 0x15) + 0x54760499) *
               0x1125f1b6;
    lVar3 = (ulonglong)param_2 * 0x5c + ((longlong)DAT_188198e08 ^ 0x2b849db3U) + DAT_1899dbaf8;
  }
  iVar4 = (int)local_48;
  if (*(int *)(lVar3 + 4) - iVar4 == 0xfbe4139) {
    lStack_40 = lVar3;
    if (param_1 != DAT_1899db1c0) {
      FUN_18042b910(param_1,&local_48);
    }
    iVar1 = *(int *)(lVar3 + 0x30);
    if ((*(uint *)(lVar3 + 0x34) ^ 0x3399efb) - iVar4 != -1) {
      uVar2 = FUN_18043ab50();
      local_48 = FUN_18043ab50((iVar1 - iVar4) + -0x4b6accc7);
      lStack_40 = uVar2;
      local_38 = param_2;
      FUN_1804201e0(*(undefined8 *)(param_1 + 8),local_28,&local_48,&local_48);
    }
  }
  return;
}



/* ================= 0x180430980 ================= */
/* name   = FUN_180430980 */
/* entry  = 180430980 */
/* body   = 1191 bytes */
/* sig    = undefined FUN_180430980() */


longlong FUN_180430980(uint param_1)

{
  byte bVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  longlong lVar5;
  undefined8 uVar6;
  uint *puVar7;
  uint *puVar8;
  uint *puVar9;
  short sVar10;
  longlong lVar11;
  int *piVar12;
  uint uVar13;
  uint *puVar15;
  uint *puVar14;
  
  lVar11 = (((ulonglong)param_1 * 0x1f17946ef935 + 0xafd81baecafdac6 >> 0x15) + 0x54760499) *
           0x1125f1b6;
  piVar12 = (int *)((ulonglong)param_1 * 0x5c +
                   ((longlong)DAT_188198e08 ^ 0x2b849db3U) + DAT_1899dbaf8);
  puVar9 = *(uint **)(PTR_PTR_1881a35f0 + (longlong)(int)param_1 * 8);
  sVar10 = (short)lVar11;
  lVar5 = FUN_1804f09a0(DAT_1899dbad0,1,
                        (ulonglong)(ushort)(((short)piVar12[0x14] - sVar10) + 0xd81a) * 0x10 + 0x148
                       );
  puVar15 = (uint *)0x0;
  if (lVar5 != 0) {
    FUN_180500080(lVar5,0,0x148);
    *(undefined8 *)(lVar5 + 200) = 0;
    *(undefined8 *)(lVar5 + 0xd0) = 0;
  }
  iVar3 = DAT_1899dbc08;
  *(longlong *)lVar5 = lVar5;
  puVar7 = puVar15;
  if (0 < iVar3) {
    puVar8 = (uint *)(DAT_1899dbc10 + 0x14);
    puVar14 = puVar15;
    do {
      if (((int)(*puVar8 ^ 0x1d3b2899) <= (int)param_1) &&
         (puVar7 = puVar8 + -5, param_1 < (puVar8[2] ^ 0x53c69178) + (*puVar8 ^ 0x1d3b2899))) break;
      uVar13 = (int)puVar14 + 1;
      puVar14 = (uint *)(ulonglong)uVar13;
      puVar8 = puVar8 + 0x14;
      puVar7 = puVar15;
    } while ((int)uVar13 < iVar3);
  }
  *(uint **)(lVar5 + 0x58) = puVar7;
  iVar4 = (int)lVar11;
  uVar6 = FUN_18043ab50((piVar12[0xd] ^ 0x3399efbU) - iVar4);
  *(undefined8 *)(lVar5 + 0xa8) = uVar6;
  uVar6 = FUN_18043ab50((piVar12[0xc] - iVar4) + -0x4b6accc7);
  *(undefined8 *)(lVar5 + 0x20) = uVar6;
  iVar3 = (piVar12[0xb] ^ 0x1f5a4501U) - iVar4;
  puVar7 = puVar15;
  if (iVar3 != -1) {
    puVar7 = *(uint **)(PTR_PTR_1881a3628 + (longlong)iVar3 * 8);
  }
  uVar6 = *(undefined8 *)(puVar7 + 2);
  *(undefined8 *)(lVar5 + 0x60) = *(undefined8 *)puVar7;
  *(undefined8 *)(lVar5 + 0x68) = uVar6;
  iVar3 = (piVar12[10] - iVar4) + -0x67ad6f69;
  puVar7 = puVar15;
  if (iVar3 != -1) {
    puVar7 = *(uint **)(PTR_PTR_1881a3628 + (longlong)iVar3 * 8);
  }
  uVar6 = *(undefined8 *)(puVar7 + 2);
  *(undefined8 *)(lVar5 + 0xb0) = *(undefined8 *)puVar7;
  *(undefined8 *)(lVar5 + 0xb8) = uVar6;
  *(longlong *)(lVar5 + 200) = lVar11;
  *(int **)(lVar5 + 0xd0) = piVar12;
  *(int *)(lVar5 + 0x108) = (piVar12[0xf] - iVar4) + -0x2303ae63;
  *(uint *)(lVar5 + 0x114) = *puVar9 ^ 0x6203cc4e;
  *(uint *)(lVar5 + 0x11c) = *puVar9 ^ 0x6203cc4e;
  *(uint *)(lVar5 + 0x100) = puVar9[2] + 0xd5afdcdb;
  *(uint *)(lVar5 + 0x110) = puVar9[3] + 0xf3c1e707;
  uVar13 = puVar9[1];
  *(undefined4 *)(lVar5 + 0x118) = 0xffffffff;
  *(uint *)(lVar5 + 0x104) = uVar13 ^ 0x10f25b04;
  *(int *)(lVar5 + 0x10c) = (piVar12[3] - iVar4) + -0x609223d6;
  *(byte *)(lVar5 + 0x142) = *(byte *)(piVar12 + 0x15) & 1;
  *(byte *)(lVar5 + 0x137) = (byte)((piVar12[0x15] - iVar4) + 0xe65638b4U >> 1) & 1;
  *(bool *)(lVar5 + 0x13e) = piVar12[0xf] - iVar4 != 0x2303ae62;
  *(byte *)(lVar5 + 0x13b) = (byte)((piVar12[0x15] - iVar4) + 0xe65638b4U >> 2) & 1;
  bVar1 = (byte)((piVar12[0x15] - iVar4) + 0xe65638b4U >> 3) & 1;
  *(byte *)(lVar5 + 0x139) = bVar1;
  *(uint *)(lVar5 + 0xe8) = bVar1 ^ 1;
  *(byte *)(lVar5 + 0x143) = (byte)((piVar12[0x15] - iVar4) + 0xe65638b4U >> 4) & 1;
  *(byte *)(lVar5 + 0x141) = (byte)((piVar12[0x15] - iVar4) + 0xe65638b4U >> 5) & 1;
  switch((piVar12[0x15] - iVar4) + 0xb4U >> 6 & 0xf) {
  default:
    uVar2 = 0;
    break;
  case 1:
    uVar2 = 1;
    break;
  case 2:
    uVar2 = 2;
    break;
  case 3:
    uVar2 = 4;
    break;
  case 4:
    uVar2 = 8;
    break;
  case 5:
    uVar2 = 0x10;
    break;
  case 6:
    uVar2 = 0x20;
    break;
  case 7:
    uVar2 = 0x40;
    break;
  case 8:
    uVar2 = 0x80;
  }
  *(undefined1 *)(lVar5 + 0x130) = uVar2;
  *(short *)(lVar5 + 0x124) = ((short)piVar12[0x12] - sVar10) + 0x1950;
  *(short *)(lVar5 + 0x126) = (*(short *)((longlong)piVar12 + 0x4a) - sVar10) + 0x17a3;
  *(short *)(lVar5 + 0x12a) = (*(short *)((longlong)piVar12 + 0x4e) - sVar10) + -2;
  *(short *)(lVar5 + 0x128) = (*(short *)((longlong)piVar12 + 0x52) - sVar10) + 0x1197;
  *(ushort *)(lVar5 + 0x122) = (*(ushort *)((longlong)piVar12 + 0x46) ^ 0x7883) - sVar10;
  *(short *)(lVar5 + 0x120) = ((short)piVar12[0x14] - sVar10) + -0x27e6;
  *(ushort *)(lVar5 + 300) = (*(ushort *)(piVar12 + 0x11) ^ 0x910a) - sVar10;
  *(ushort *)(lVar5 + 0x12e) = (*(ushort *)(piVar12 + 0x13) ^ 0x5be4) - sVar10;
  *(uint *)(lVar5 + 0xf8) = (piVar12[0x16] ^ 0x78647f39U) - iVar4;
  uVar6 = FUN_180436810(lVar5 + 0x60);
  *(undefined8 *)(lVar5 + 0x48) = uVar6;
  iVar3 = (*piVar12 - iVar4) + -0x15f045cb;
  if (iVar3 != -1) {
    uVar6 = FUN_180430150(*(undefined8 *)(PTR_PTR_1881a3628 + (longlong)iVar3 * 8),1);
    *(undefined8 *)(lVar5 + 0x80) = uVar6;
  }
  if (piVar12[1] - iVar4 != 0xfbe4139) {
    iVar3 = (piVar12[1] - iVar4) + -0xfbe413a;
    puVar9 = puVar15;
    if (iVar3 != -1) {
      puVar9 = *(uint **)(PTR_PTR_1881a3628 + (longlong)iVar3 * 8);
    }
    uVar6 = FUN_180430150(puVar9,1);
    *(undefined8 *)(lVar5 + 0x88) = uVar6;
  }
  *(longlong *)(lVar5 + 0x30) = lVar5;
  *(longlong *)(lVar5 + 0x98) = lVar5;
  if (*(char *)(lVar5 + 0x137) != '\0') {
    iVar4 = (piVar12[0x10] ^ 0x5aeb04U) - iVar4;
    if (iVar4 != -1) {
      puVar15 = *(uint **)(PTR_PTR_1881a3628 + (longlong)iVar4 * 8);
    }
    uVar6 = FUN_180430150(puVar15,1);
    *(undefined8 *)(lVar5 + 0x30) = uVar6;
    *(undefined8 *)(lVar5 + 0x98) = uVar6;
  }
  return lVar5;
}



/* ================= 0x180438290 ================= */
/* name   = FUN_180438290 */
/* entry  = 180438290 */
/* body   = 3088 bytes */
/* sig    = undefined FUN_180438290() */


void FUN_180438290(undefined8 *param_1,uint *param_2,int param_3,char param_4)

{
  char cVar1;
  uint *puVar2;
  uint uVar3;
  int iVar4;
  char *pcVar5;
  char *pcVar6;
  undefined8 *puVar7;
  uint uVar8;
  ulonglong *puVar9;
  ulonglong uVar10;
  ulonglong uVar11;
  undefined8 uVar12;
  longlong lVar13;
  ulonglong uVar14;
  undefined4 uVar15;
  ulonglong local_68;
  uint *local_60;
  undefined8 local_58;
  ulonglong local_50;
  longlong local_48;
  ulonglong local_40;
  longlong local_38;
  undefined8 local_30;
  ulonglong local_28;
  undefined8 local_20;
  
  local_20 = 0xfffffffffffffffe;
  uVar10 = 0;
  uVar15 = 0;
  cVar1 = *(char *)((longlong)param_2 + 10);
  if (cVar1 == '\x0f') {
    iVar4 = param_3;
    if (param_3 == 3) {
      iVar4 = 2;
    }
    FUN_180438290(param_1,*(undefined8 *)param_2,iVar4,0,0);
    FUN_1803f8f80(param_1,1,0x2a);
    if ((param_2[2] & 0x40000000) != 0) {
      FUN_1803f8f80(param_1,1,0x26);
    }
    if (param_3 != 3) {
      return;
    }
    lVar13 = FUN_180430150(*(undefined8 *)param_2,1);
    uVar12 = FUN_18042c890(&local_40,
                           (*(ulonglong *)(*(longlong *)(lVar13 + 0x58) + 0x38) ^ 0x563412751289b3d9
                           ) + 0x18);
    uVar12 = FUN_1803fac40(&local_68,&DAT_188195204,uVar12);
    FUN_1803f8d00(param_1,uVar12,0,0xffffffffffffffff);
    FUN_1803ed580(&local_68);
    goto LAB_180438e98;
  }
  if (cVar1 == '\x13') {
LAB_180438d42:
    uVar3 = *param_2;
    uVar11 = uVar10;
    uVar14 = uVar10;
    if (uVar3 != 0xffffffff) {
      uVar11 = ((ulonglong)uVar3 * 0x34d04ba0e4db + 0xa13ee8c44cc682a ^ 0x43427e7d) + 0x10776301;
      uVar14 = (ulonglong)uVar3 * 0x10 + (DAT_188198e40 + -0x77870e75) + DAT_1899dbaf8;
    }
    pcVar6 = (char *)FUN_18043ab50(*(int *)(uVar14 + 4) + 0xee50a144U ^ (uint)uVar11);
    if (*pcVar6 != '\0') {
      uVar10 = 0xffffffffffffffff;
      do {
        uVar10 = uVar10 + 1;
      } while (pcVar6[uVar10] != '\0');
    }
    FUN_1803f8e30(param_1,pcVar6,uVar10);
    if ((param_2[2] & 0x40000000) == 0) {
      return;
    }
    FUN_1803f8f80(param_1,1,0x26);
    return;
  }
  if (cVar1 != '\x14') {
    if (cVar1 == '\x1d') {
      local_68 = FUN_180430150(*(undefined8 *)param_2,1);
      iVar4 = param_3;
      if (param_3 == 3) {
        iVar4 = 2;
      }
      FUN_180438290(param_1,local_68 + 0x60,iVar4,0);
      FUN_1803f8e30(param_1,&DAT_1881a2f78,2);
      if ((param_2[2] & 0x40000000) != 0) {
        if ((ulonglong)~param_1[2] < 2) {
                    /* WARNING: Subroutine does not return */
          FUN_1804fe5b8("string too long");
        }
        uVar10 = param_1[2] + 1;
        if (uVar10 == 0xffffffffffffffff) {
                    /* WARNING: Subroutine does not return */
          FUN_1804fe5b8("string too long");
        }
        if ((ulonglong)param_1[3] < uVar10) {
          FUN_1803f80b0(param_1,uVar10);
LAB_180438806:
          if (uVar10 == 0) goto LAB_180438839;
        }
        else if (uVar10 == 0) {
          param_1[2] = 0;
          puVar7 = param_1;
          if (0xf < (ulonglong)param_1[3]) {
            puVar7 = (undefined8 *)*param_1;
          }
          *(undefined1 *)puVar7 = 0;
          goto LAB_180438806;
        }
        puVar7 = param_1;
        if (0xf < (ulonglong)param_1[3]) {
          puVar7 = (undefined8 *)*param_1;
        }
        *(undefined1 *)((longlong)puVar7 + param_1[2]) = 0x26;
        param_1[2] = uVar10;
        puVar7 = param_1;
        if (0xf < (ulonglong)param_1[3]) {
          puVar7 = (undefined8 *)*param_1;
        }
        *(undefined1 *)(uVar10 + (longlong)puVar7) = 0;
      }
LAB_180438839:
      if (param_3 != 3) {
        return;
      }
      uVar12 = FUN_18042c890(&local_40,
                             (*(ulonglong *)(*(longlong *)(local_68 + 0x58) + 0x38) ^
                             0x563412751289b3d9) + 0x18);
      uVar12 = FUN_1803fac40(&local_68,&DAT_188195204,uVar12);
      FUN_1803f8d00(param_1,uVar12,0,0xffffffffffffffff);
      FUN_1803ed580(&local_68);
      goto LAB_180438e98;
    }
    if (cVar1 == '\x1e') goto LAB_180438d42;
    local_48 = FUN_180430150(param_2,1);
    uVar3 = 1;
    if (*(longlong *)(local_48 + 0x88) == 0) {
      if (**(char **)(local_48 + 0x20) != '\0') {
        lVar13 = -1;
        do {
          lVar13 = lVar13 + 1;
        } while ((*(char **)(local_48 + 0x20))[lVar13] != '\0');
        FUN_1803f8e30(param_1);
        goto LAB_18043835a;
      }
    }
    else {
      FUN_180438290(param_1,*(longlong *)(local_48 + 0x88) + 0x60,param_3,1,uVar15);
LAB_18043835a:
      FUN_1803f8f80(param_1,1);
    }
    if (param_3 == 0) {
      pcVar5 = (char *)FUN_180501f84(*(undefined8 *)(local_48 + 0xa8),0x60);
      pcVar6 = *(char **)(local_48 + 0xa8);
      if (pcVar5 == (char *)0x0) {
        local_50 = 0xf;
        local_58 = 0;
        local_68 = local_68 & 0xffffffffffffff00;
        uVar11 = uVar10;
        if (*pcVar6 != '\0') {
          uVar11 = 0xffffffffffffffff;
          do {
            uVar11 = uVar11 + 1;
          } while (pcVar6[uVar11] != '\0');
        }
        FUN_1803f92e0(&local_68,pcVar6,uVar11);
        puVar9 = &local_68;
        uVar3 = 2;
      }
      else {
        local_28 = 0xf;
        local_30 = 0;
        local_40 = local_40 & 0xffffffffffffff00;
        if (pcVar6 != pcVar5) {
          FUN_1803f92e0(&local_40,pcVar6,(longlong)pcVar5 - (longlong)pcVar6);
        }
        puVar9 = &local_40;
      }
      FUN_1803f8d00(param_1,puVar9,0,0xffffffffffffffff,uVar3);
      if ((uVar3 & 2) != 0) {
        uVar3 = uVar3 & 0xfffffffd;
        FUN_1803ed580(&local_68);
      }
      if ((uVar3 & 1) != 0) {
        FUN_1803ed580(&local_40);
      }
    }
    else {
      pcVar6 = *(char **)(local_48 + 0xa8);
      uVar11 = uVar10;
      if (*pcVar6 != '\0') {
        uVar11 = 0xffffffffffffffff;
        do {
          uVar11 = uVar11 + 1;
        } while (pcVar6[uVar11] != '\0');
      }
      FUN_1803f8e30(param_1,pcVar6,uVar11);
    }
    if (param_4 != '\0') {
      return;
    }
    if (*(longlong *)(local_48 + 0xc0) == 0) {
      if ((*(char *)(local_48 + 0x13e) != '\0') && (1 < param_3 - 2U)) {
        FUN_1804358c0(&local_68,*(undefined4 *)(local_48 + 0x108));
        FUN_1803f8f80(param_1,1);
        uVar3 = 0;
        if (0 < (int)((*local_60 ^ 0x13c7ef8b) - (int)local_68)) {
          do {
            iVar4 = (int)local_68;
            uVar8 = 0;
            if ((int)uVar10 != 0) {
              uVar8 = uVar3;
              FUN_1803f8f80(param_1,1);
              iVar4 = (int)local_68;
              uVar3 = uVar8;
            }
            FUN_180435f40(&local_40,(uVar8 & 0xffff) + ((local_60[2] + 0xbdf95d6f) - iVar4));
            pcVar6 = (char *)FUN_18043ab50(*(int *)(local_38 + 4) + 0xee50a144U ^ (uint)local_40);
            if (*pcVar6 != '\0') {
              lVar13 = -1;
              do {
                lVar13 = lVar13 + 1;
              } while (pcVar6[lVar13] != '\0');
            }
            FUN_1803f8e30(param_1,pcVar6);
            uVar3 = uVar3 + 1;
            uVar10 = (ulonglong)uVar3;
          } while ((int)uVar3 < (int)((*local_60 ^ 0x13c7ef8b) - (int)local_68));
        }
        uVar12 = 0x5d;
        if (param_3 == 0) {
          uVar12 = 0x3e;
        }
        FUN_1803f8f80(param_1,1,uVar12);
      }
    }
    else {
      puVar2 = *(uint **)(*(longlong *)(local_48 + 0xc0) + 8);
      iVar4 = param_3;
      if (param_3 == 2) {
        iVar4 = 3;
      }
      uVar12 = 0x5b;
      if (param_3 == 0) {
        uVar12 = 0x3c;
      }
      FUN_1803f8f80(param_1,1,uVar12);
      if (*puVar2 != 0) {
        do {
          local_68 = uVar10 * 8;
          local_40 = *(ulonglong *)(local_68 + *(longlong *)(puVar2 + 2));
          if ((int)uVar10 != 0) {
            FUN_1803f8f80(param_1,1,0x2c);
          }
          if (((iVar4 == 3) && (*(char *)(local_40 + 10) != '\x13')) &&
             (*(char *)((longlong)param_2 + 10) != '\x1e')) {
            FUN_1803f8f80(param_1,1,0x5b);
          }
          FUN_180438290(param_1,*(undefined8 *)(local_68 + *(longlong *)(puVar2 + 2)),iVar4,0);
          if (((iVar4 == 3) && (*(char *)(local_40 + 10) != '\x13')) &&
             (*(char *)((longlong)param_2 + 10) != '\x1e')) {
            FUN_1803f8f80(param_1,1,0x5d);
          }
          uVar3 = (int)uVar10 + 1;
          uVar10 = (ulonglong)uVar3;
        } while (uVar3 < *puVar2);
      }
      uVar12 = 0x5d;
      if (param_3 == 0) {
        uVar12 = 0x3e;
      }
      FUN_1803f8f80(param_1,1,uVar12);
    }
    if ((param_2[2] & 0x40000000) != 0) {
      FUN_1803f8f80(param_1,1,0x26);
    }
    if (param_3 != 3) {
      return;
    }
    if (*(char *)((longlong)param_2 + 10) == '\x13') {
      return;
    }
    if (*(char *)((longlong)param_2 + 10) == '\x1e') {
      return;
    }
    uVar12 = FUN_18042c890(&local_40,
                           (*(ulonglong *)(*(longlong *)(local_48 + 0x58) + 0x38) ^
                           0x563412751289b3d9) + 0x18);
    uVar12 = FUN_1803fac40(&local_68,&DAT_188195204,uVar12);
    FUN_1803f8d00(param_1,uVar12,0,0xffffffffffffffff);
    FUN_1803ed580(&local_68);
LAB_180438e98:
    FUN_1803ed580(&local_40);
    return;
  }
  lVar13 = FUN_180430150(param_2,1);
  local_68 = *(ulonglong *)(lVar13 + 0x30);
  iVar4 = param_3;
  if (param_3 == 3) {
    iVar4 = 2;
  }
  FUN_180438290(param_1,local_68 + 0x60,iVar4,0);
  if ((ulonglong)~param_1[2] < 2) {
                    /* WARNING: Subroutine does not return */
    FUN_1804fe5b8("string too long");
  }
  uVar10 = param_1[2] + 1;
  if (uVar10 == 0xffffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_1804fe5b8("string too long");
  }
  if ((ulonglong)param_1[3] < uVar10) {
    FUN_1803f80b0(param_1,uVar10);
LAB_180438938:
    if (uVar10 != 0) goto LAB_18043893d;
  }
  else {
    if (uVar10 == 0) {
      param_1[2] = 0;
      puVar7 = param_1;
      if (0xf < (ulonglong)param_1[3]) {
        puVar7 = (undefined8 *)*param_1;
      }
      *(undefined1 *)puVar7 = 0;
      goto LAB_180438938;
    }
LAB_18043893d:
    puVar7 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar7 = (undefined8 *)*param_1;
    }
    *(undefined1 *)((longlong)puVar7 + param_1[2]) = 0x5b;
    param_1[2] = uVar10;
    puVar7 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar7 = (undefined8 *)*param_1;
    }
    *(undefined1 *)((longlong)puVar7 + uVar10) = 0;
  }
  if (*(char *)(lVar13 + 0x131) == '\x01') {
    if ((ulonglong)~param_1[2] < 2) {
                    /* WARNING: Subroutine does not return */
      FUN_1804fe5b8("string too long");
    }
    uVar10 = param_1[2] + 1;
    if (uVar10 == 0xffffffffffffffff) {
                    /* WARNING: Subroutine does not return */
      FUN_1804fe5b8("string too long");
    }
    if ((ulonglong)param_1[3] < uVar10) {
      FUN_1803f80b0(param_1,uVar10);
LAB_1804389e3:
      if (uVar10 == 0) goto LAB_180438a16;
    }
    else if (uVar10 == 0) {
      param_1[2] = 0;
      puVar7 = param_1;
      if (0xf < (ulonglong)param_1[3]) {
        puVar7 = (undefined8 *)*param_1;
      }
      *(undefined1 *)puVar7 = 0;
      goto LAB_1804389e3;
    }
    puVar7 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar7 = (undefined8 *)*param_1;
    }
    *(undefined1 *)((longlong)puVar7 + param_1[2]) = 0x2a;
    param_1[2] = uVar10;
    puVar7 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar7 = (undefined8 *)*param_1;
    }
    *(undefined1 *)((longlong)puVar7 + uVar10) = 0;
  }
LAB_180438a16:
  local_40 = 1;
  if (1 < *(byte *)(lVar13 + 0x131)) {
    do {
      iVar4 = (int)local_40;
      if ((ulonglong)~param_1[2] < 2) {
                    /* WARNING: Subroutine does not return */
        FUN_1804fe5b8("string too long");
      }
      uVar10 = param_1[2] + 1;
      if (uVar10 == 0xffffffffffffffff) {
                    /* WARNING: Subroutine does not return */
        FUN_1804fe5b8("string too long");
      }
      if ((ulonglong)param_1[3] < uVar10) {
        FUN_1803f80b0(param_1,uVar10);
        iVar4 = (int)local_40;
LAB_180438a88:
        if (uVar10 != 0) goto LAB_180438a8d;
      }
      else {
        if (uVar10 == 0) {
          param_1[2] = 0;
          puVar7 = param_1;
          if (0xf < (ulonglong)param_1[3]) {
            puVar7 = (undefined8 *)*param_1;
          }
          *(undefined1 *)puVar7 = 0;
          goto LAB_180438a88;
        }
LAB_180438a8d:
        puVar7 = param_1;
        if (0xf < (ulonglong)param_1[3]) {
          puVar7 = (undefined8 *)*param_1;
        }
        *(undefined1 *)(param_1[2] + (longlong)puVar7) = 0x2c;
        param_1[2] = uVar10;
        puVar7 = param_1;
        if (0xf < (ulonglong)param_1[3]) {
          puVar7 = (undefined8 *)*param_1;
        }
        *(undefined1 *)(uVar10 + (longlong)puVar7) = 0;
      }
      local_40 = (ulonglong)(iVar4 + 1U);
    } while ((int)(iVar4 + 1U) < (int)(uint)*(byte *)(lVar13 + 0x131));
  }
  if ((ulonglong)~param_1[2] < 2) {
                    /* WARNING: Subroutine does not return */
    FUN_1804fe5b8("string too long");
  }
  uVar10 = param_1[2] + 1;
  if (uVar10 == 0xffffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_1804fe5b8("string too long");
  }
  if ((ulonglong)param_1[3] < uVar10) {
    FUN_1803f80b0(param_1,uVar10);
LAB_180438b4f:
    if (uVar10 != 0) goto LAB_180438b54;
  }
  else {
    if (uVar10 == 0) {
      param_1[2] = 0;
      puVar7 = param_1;
      if (0xf < (ulonglong)param_1[3]) {
        puVar7 = (undefined8 *)*param_1;
      }
      *(undefined1 *)puVar7 = 0;
      goto LAB_180438b4f;
    }
LAB_180438b54:
    puVar7 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar7 = (undefined8 *)*param_1;
    }
    *(undefined1 *)(param_1[2] + (longlong)puVar7) = 0x5d;
    param_1[2] = uVar10;
    puVar7 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar7 = (undefined8 *)*param_1;
    }
    *(undefined1 *)(uVar10 + (longlong)puVar7) = 0;
  }
  if ((param_2[2] & 0x40000000) == 0) goto LAB_180438c28;
  if ((ulonglong)~param_1[2] < 2) {
                    /* WARNING: Subroutine does not return */
    FUN_1804fe5b8("string too long");
  }
  uVar10 = param_1[2] + 1;
  if (uVar10 == 0xffffffffffffffff) {
                    /* WARNING: Subroutine does not return */
    FUN_1804fe5b8("string too long");
  }
  if ((ulonglong)param_1[3] < uVar10) {
    FUN_1803f80b0(param_1,uVar10);
LAB_180438bf5:
    if (uVar10 == 0) goto LAB_180438c28;
  }
  else if (uVar10 == 0) {
    param_1[2] = 0;
    puVar7 = param_1;
    if (0xf < (ulonglong)param_1[3]) {
      puVar7 = (undefined8 *)*param_1;
    }
    *(undefined1 *)puVar7 = 0;
    goto LAB_180438bf5;
  }
  puVar7 = param_1;
  if (0xf < (ulonglong)param_1[3]) {
    puVar7 = (undefined8 *)*param_1;
  }
  *(undefined1 *)(param_1[2] + (longlong)puVar7) = 0x26;
  param_1[2] = uVar10;
  puVar7 = param_1;
  if (0xf < (ulonglong)param_1[3]) {
    puVar7 = (undefined8 *)*param_1;
  }
  *(undefined1 *)(uVar10 + (longlong)puVar7) = 0;
LAB_180438c28:
  if (param_3 == 3) {
    uVar12 = FUN_18042c890(&local_40,
                           (*(ulonglong *)(*(longlong *)(local_68 + 0x58) + 0x38) ^
                           0x563412751289b3d9) + 0x18);
    uVar12 = FUN_1803fac40(&local_68,&DAT_188195204,uVar12);
    FUN_1803f8d00(param_1,uVar12,0,0xffffffffffffffff);
    if (0xf < local_50) {
      uVar10 = local_68;
      if (0xfff < local_50 + 1) {
        if ((local_68 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        uVar10 = *(ulonglong *)(local_68 - 8);
        if (local_68 <= uVar10) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if (local_68 - uVar10 < 8) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if (0x27 < local_68 - uVar10) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
      }
      thunk_FUN_18050a3b8(uVar10);
    }
    local_50 = 0xf;
    local_58 = 0;
    local_68 = local_68 & 0xffffffffffffff00;
    if (0xf < local_28) {
      uVar10 = local_40;
      if (0xfff < local_28 + 1) {
        if ((local_40 & 0x1f) != 0) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        uVar10 = *(ulonglong *)(local_40 - 8);
        if (local_40 <= uVar10) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if (local_40 - uVar10 < 8) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
        if (0x27 < local_40 - uVar10) {
                    /* WARNING: Subroutine does not return */
          FUN_180509dc8();
        }
      }
      thunk_FUN_18050a3b8(uVar10);
    }
  }
  return;
}



/* ================= 0x180406056 ================= */
/* name   = FUN_180406010 */
/* entry  = 180406010 */
/* body   = 461 bytes */
/* sig    = undefined FUN_180406010() */


undefined8 * FUN_180406010(longlong param_1)

{
  char cVar1;
  int iVar2;
  undefined8 *puVar3;
  undefined8 uVar4;
  undefined8 *puVar5;
  ulonglong uVar6;
  ushort local_38;
  undefined2 uStack_36;
  uint *local_30;
  undefined4 local_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  puVar5 = (undefined8 *)0x0;
  cVar1 = *(char *)((longlong)*(undefined4 **)(param_1 + 0x10) + 10);
  puVar3 = puVar5;
  if ((((cVar1 == '\x13') || (cVar1 == '\x1e')) &&
      (FUN_180435f40(&local_38,**(undefined4 **)(param_1 + 0x10)), local_30 != (uint *)0x0)) &&
     (puVar3 = (undefined8 *)FUN_180438170(), puVar3 == (undefined8 *)0x0)) {
    puVar3 = (undefined8 *)_malloc_base(0x20);
    *(ushort *)(puVar3 + 2) = *(short *)((longlong)local_30 + 10) - 0x7e2U ^ local_38;
    *(uint *)((longlong)puVar3 + 0x14) = (ushort)((ushort)local_30[3] ^ local_38) ^ 0x5910;
    uVar4 = FUN_18043ab50(local_30[1] + 0xee50a144 ^ CONCAT22(uStack_36,local_38));
    puVar3[1] = uVar4;
    FUN_1804358c0(&local_28,*local_30 ^ CONCAT22(uStack_36,local_38) ^ 0x6fe8ee1b);
    *puVar3 = 0;
    if (CONCAT44(uStack_1c,uStack_20) != 0) {
      local_18 = local_28;
      uStack_14 = uStack_24;
      uStack_10 = uStack_20;
      uStack_c = uStack_1c;
      uVar4 = FUN_180433e30(&local_18);
      *puVar3 = uVar4;
    }
    uVar4 = _malloc_base((longlong)
                         (int)(((int)(short)(local_38 ^ (ushort)local_30[2]) ^ 0xffffc6bdU) + 1) <<
                         3);
    puVar3[3] = uVar4;
    uVar6 = (ulonglong)CONCAT22(uStack_36,local_38);
    if (0 < (short)((ushort)local_30[2] ^ local_38 ^ 0xc6bd)) {
      do {
        iVar2 = (int)puVar5;
        uVar4 = FUN_180435f00(iVar2 + ((uint)CONCAT62((int6)(uVar6 >> 0x10),
                                                      (ushort)uVar6 ^
                                                      *(ushort *)((longlong)local_30 + 0xe)) ^
                                      0x2522));
        uVar4 = FUN_180430150(uVar4,1);
        puVar5 = (undefined8 *)(ulonglong)(iVar2 + 1U);
        *(undefined8 *)(puVar3[3] + (longlong)iVar2 * 8) = uVar4;
        uVar6 = (ulonglong)CONCAT22(uStack_36,local_38);
      } while ((int)(iVar2 + 1U) < (int)((int)(short)((ushort)local_30[2] ^ local_38) ^ 0xffffc6bdU)
              );
    }
    *(undefined8 *)
     (puVar3[3] + ((longlong)(short)((ushort)local_30[2] ^ (ushort)uVar6) ^ 0xffffffffffffc6bdU) * 8
     ) = 0;
    FUN_18044ab70(local_30,puVar3);
    return puVar3;
  }
  return puVar3;
}



/* ================= 0x18042FE20 ================= */
/* name   = FUN_18042fe20 */
/* entry  = 18042fe20 */
/* body   = 802 bytes */
/* sig    = undefined FUN_18042fe20() */


ulonglong FUN_18042fe20(uint *param_1)

{
  byte bVar1;
  undefined4 uVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  undefined8 uVar5;
  int iVar6;
  ulonglong *puVar7;
  ulonglong uVar8;
  ulonglong uVar9;
  longlong *plVar10;
  ulonglong *puVar11;
  longlong lVar12;
  ulonglong *puVar13;
  uint uVar14;
  int iVar15;
  undefined8 local_60;
  ulonglong local_58;
  undefined1 local_50 [24];
  
  FUN_1803f4990(&DAT_1899db6b0);
  uVar4 = *(ulonglong *)(param_1 + 2);
  uVar9 = DAT_1899db658 & uVar4;
  puVar13 = (ulonglong *)0x0;
  iVar15 = 0;
  uVar8 = DAT_1899db658;
  puVar11 = puVar13;
  do {
    lVar12 = (uVar9 >> 6) * 0x20;
    plVar10 = (longlong *)(DAT_1899db678 + lVar12);
    uVar3 = 1L << ((byte)uVar9 & 0x3f);
    if ((plVar10[1] & uVar3) == 0) {
      lVar12 = DAT_1899db668;
      puVar7 = puVar13;
      if (((plVar10[2] & uVar3) == 0) || (DAT_1899db680 <= puVar11)) goto LAB_18042ff01;
    }
    else {
      bVar1 = FUN_180415ac0(uVar3 - 1 & plVar10[1]);
      puVar7 = (ulonglong *)((ulonglong)bVar1 * 0x10 + *plVar10);
      uVar8 = DAT_1899db658;
      if (uVar4 == *puVar7) {
        lVar12 = lVar12 + DAT_1899db660;
LAB_18042ff01:
        if (((lVar12 - DAT_1899db660 & 0xffffffffffffffe0U) + DAT_1899db660 == DAT_1899db668) &&
           (puVar7 == (ulonglong *)0x0)) {
          uVar4 = FUN_1804f09a0(DAT_1899dbad0,1,0x148);
          if (uVar4 != 0) {
            FUN_180500080(uVar4,0,0x148);
            *(undefined8 *)(uVar4 + 200) = 0;
            *(undefined8 *)(uVar4 + 0xd0) = 0;
          }
          *(ulonglong *)uVar4 = uVar4;
          uVar5 = FUN_18043ab50(*(int *)(*(longlong *)(param_1 + 2) + 4) + 0xee50a144U ^ *param_1);
          *(undefined8 *)(uVar4 + 0xa8) = uVar5;
          *(undefined1 **)(uVar4 + 0x20) = &DAT_187aebda5;
          uVar14 = (uint)*(undefined8 *)param_1 ^ **(uint **)(param_1 + 2) ^ 0x6fe8ee1b;
          if (uVar14 != 0xffffffff) {
            iVar15 = ((uint)((((ulonglong)uVar14 * 0x6ae9 ^ 0x2e6f3e3d) * 0x2ad3dd28 >> 0x16) *
                             0x4c39b37d >> 10) ^ 0x4dfaa6b0) * 0x22449c6e;
            puVar13 = (ulonglong *)
                      ((ulonglong)uVar14 * 0x10 + (int)(DAT_188198e00 ^ 0x7497c9ee) + DAT_1899dbaf8)
            ;
          }
          if (*(int *)((longlong)puVar13 + 0xc) + -0x175a3fdf == iVar15) {
            lVar12 = FUN_18043b320((*(int *)((longlong)puVar13 + 4) + -0x1df344f8) - iVar15);
          }
          else {
            plVar10 = (longlong *)FUN_180437120();
            lVar12 = *plVar10;
          }
          *(undefined8 *)(uVar4 + 0x58) = *(undefined8 *)(lVar12 + 0x58);
          *(undefined1 *)(uVar4 + 0x13f) = 1;
          *(bool *)(uVar4 + 0x136) = *(char *)(uVar4 + 0x13d) == '\0';
          *(undefined8 *)(uVar4 + 0x80) = DAT_1899db1c8;
          *(ulonglong *)(uVar4 + 0x30) = uVar4;
          *(ulonglong *)(uVar4 + 0x98) = uVar4;
          *(undefined4 *)(uVar4 + 0x10c) = 1;
          iVar6 = 0x13;
          if (*(int *)((longlong)puVar13 + 0xc) + -0x175a3fdf != iVar15) {
            iVar6 = 0x1e;
          }
          *(uint *)(uVar4 + 0x68) = iVar6 << 0x10 | *(uint *)(uVar4 + 0x68) & 0xff00ffff;
          *(char *)(uVar4 + 0xba) = (char)iVar6;
          uVar2 = (undefined4)
                  (*(longlong *)(param_1 + 2) - ((DAT_188198e40 + -0x77870e75) + DAT_1899dbaf8) >> 4
                  );
          *(undefined4 *)(uVar4 + 0x60) = uVar2;
          *(undefined4 *)(uVar4 + 0xb0) = uVar2;
          *(uint *)(uVar4 + 0xb8) = *(uint *)(uVar4 + 0xb8) | 0x40000000;
          *(undefined4 *)(uVar4 + 0x114) = 8;
          *(undefined8 *)(uVar4 + 0x100) = 0xffffffffffffffff;
          *(undefined1 *)(uVar4 + 0x138) = 1;
          *(undefined1 *)(uVar4 + 0x132) = 1;
          local_60 = *(undefined8 *)(param_1 + 2);
          local_58 = uVar4;
          FUN_18041fc70(&DAT_1899db650,local_50,&local_60,&local_60);
        }
        else {
          uVar4 = puVar7[1];
        }
        FUN_1803f72c0(&DAT_1899db6b0);
        return uVar4;
      }
    }
    puVar11 = (ulonglong *)((longlong)puVar11 + 1);
    uVar9 = uVar9 + (longlong)puVar11 & uVar8;
  } while( true );
}



/* ================= 0x180434E50 ================= */
/* name   = FUN_180434e50 */
/* entry  = 180434e50 */
/* body   = 267 bytes */
/* sig    = undefined FUN_180434e50() */


ulonglong FUN_180434e50(longlong *param_1)

{
  ulonglong *puVar1;
  longlong lVar2;
  ulonglong uVar3;
  uint uVar4;
  
  FUN_1803f4990(&DAT_1899db6b0);
  puVar1 = (ulonglong *)(param_1 + 1);
  if (*puVar1 == 0x73ecc7d44725af21) {
    lVar2 = *param_1;
    if (*(longlong *)(lVar2 + -0x6381435a109016c9) == 0) {
      uVar4 = ((*(int *)(*(longlong *)(lVar2 + -0x6381435a109016b9) + 0x1c) + -0x55909af2) -
              *(int *)(lVar2 + -0x6381435a109016c1)) +
              (int)((longlong)param_1 - *(longlong *)(lVar2 + -0x6381435a10901779) >> 5);
      uVar3 = FUN_18043ab50((*(uint *)((DAT_188198e84 + -0x2f59fe76) + DAT_1899dbaf8 + 8 +
                                      (ulonglong)uVar4 * 0xc) ^ 0x5daab140) -
                            (int)((ulonglong)uVar4 * 0x7740eeff55f40540 + 0x49ed7f5afcc4af8 >> 0x11)
                           );
      *puVar1 = uVar3 ^ 0x73ecc7d44725af21;
    }
    else {
      FUN_18044b540(param_1);
    }
  }
  uVar3 = *puVar1;
  FUN_1803f72c0(&DAT_1899db6b0);
  return uVar3 ^ 0x73ecc7d44725af21;
}



/* ================= 0x1804361A0 ================= */
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



/* ================= 0x180440A35 ================= */
/* name   = FUN_1804409f0 */
/* entry  = 1804409f0 */
/* body   = 283 bytes */
/* sig    = undefined FUN_1804409f0() */


void FUN_1804409f0(void)

{
  int iVar1;
  bool bVar2;
  undefined8 uVar3;
  longlong lVar4;
  longlong lVar5;
  undefined8 uVar6;
  ulonglong uVar7;
  longlong lVar8;
  longlong lVar9;
  undefined8 local_48;
  longlong local_40;
  longlong local_38;
  undefined8 local_30;
  undefined1 local_28 [32];
  
  lVar8 = 0;
  lVar9 = (DAT_188198e98 + -0x56ca4fe4) + DAT_1899dbaf8;
  uVar7 = (longlong)(int)((ulonglong)(longlong)DAT_188198e88 >> 3) ^ 0xd9bea51;
  if (0 < (longlong)uVar7) {
    do {
      uVar3 = FUN_18043ab50(*(undefined4 *)(lVar9 + lVar8 * 8));
      iVar1 = *(int *)(lVar9 + 4 + lVar8 * 8);
      if (iVar1 == -1) {
        uVar6 = 0;
      }
      else {
        uVar6 = *(undefined8 *)(PTR_PTR_1881a3628 + (longlong)iVar1 * 8);
      }
      lVar4 = FUN_180430150(uVar6,1);
      if ((*(longlong *)(lVar4 + 0xc0) == 0) || (lVar5 = FUN_18043b320(), lVar5 != DAT_1899db360)) {
        bVar2 = false;
      }
      else {
        bVar2 = true;
      }
      if (!bVar2) {
        local_48 = uVar3;
        local_40 = lVar4;
        FUN_18041f500(&DAT_1899db880,local_28,&local_48,&local_48);
      }
      local_38 = lVar4;
      local_30 = uVar3;
      FUN_180420ec0(&DAT_1899db580,local_28,&local_38,&local_38);
      lVar8 = lVar8 + 1;
    } while (lVar8 < (longlong)uVar7);
  }
  return;
}



/* ================= 0x18044B296 ================= */
/* name   = FUN_18044b230 */
/* entry  = 18044b230 */
/* body   = 772 bytes */
/* sig    = undefined FUN_18044b230() */


void FUN_18044b230(longlong param_1,undefined8 param_2)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  undefined8 uVar4;
  longlong lVar5;
  undefined8 *puVar6;
  ulonglong uVar7;
  longlong lVar8;
  uint uVar9;
  longlong *plVar10;
  uint uVar11;
  ulonglong uVar12;
  
  if (*(longlong *)(param_1 + 0xa0) == 0) {
    if (*(undefined4 **)(param_1 + 0xc0) != (undefined4 *)0x0) {
      uVar4 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
      FUN_18044b230(uVar4,param_2);
      FUN_18044b0d0(param_1);
      return;
    }
    if ((*(char *)(param_1 + 0x131) == '\0') && (*(short *)(param_1 + 0x128) != 0)) {
      FUN_18044c400();
      uVar12 = (ulonglong)*(ushort *)(param_1 + 0x128);
      lVar5 = FUN_1804f09a0(DAT_1899dbad0,uVar12);
      uVar7 = 0;
      if (uVar12 != 0) {
        do {
          puVar6 = (undefined8 *)(uVar7 * 0x38 + lVar5);
          if (puVar6 != (undefined8 *)0x0) {
            puVar6[6] = 0;
            *puVar6 = 0x32fb1e713e9f1dd1;
            puVar6[1] = 0x4d3684112594d308;
            puVar6[2] = 0x7b0de6e70c06b3d8;
            puVar6[3] = 0x1b89658f1f964a0c;
            puVar6[4] = 0x590c54033e736b67;
            puVar6[5] = 0x17c2856111b08173;
            *(undefined4 *)(puVar6 + 6) = 0x3081751a;
          }
          uVar7 = uVar7 + 1;
        } while (uVar7 < uVar12);
      }
      uVar9 = (*(uint *)(*(longlong *)(param_1 + 0xd0) + 0x18) ^ 0x689a417f) -
              *(int *)(param_1 + 200);
      iVar2 = *(ushort *)(param_1 + 0x128) + uVar9;
      if ((int)uVar9 < iVar2) {
        plVar10 = (longlong *)(lVar5 + 8);
        do {
          uVar7 = (ulonglong)uVar9;
          uVar11 = (int)(((uVar7 * 0x7a00 ^ 0x3b79566a) * 0x3ea7abc3 ^ 0x52121a98000) >> 0xc) *
                   0x20cf3f69;
          lVar8 = ((longlong)DAT_188198e24 ^ 0x3a73133eU) + DAT_1899dbaf8;
          piVar1 = (int *)(lVar8 + uVar7 * 0x18);
          uVar3 = *(int *)(lVar8 + 0xc + uVar7 * 0x18) + 0xfcc28a65U ^ uVar11;
          if (uVar3 == 0xffffffff) {
            lVar8 = 0;
          }
          else {
            lVar8 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)(int)uVar3 * 8);
          }
          plVar10[3] = lVar8 + 0x590c54033e736b67;
          lVar8 = FUN_18043ab50(uVar11 ^ piVar1[4] + 0xbfc65639U);
          plVar10[-1] = lVar8 + 0x32fb1e713e9f1dd1;
          *plVar10 = param_1 + 0x4d3684112594d308;
          if ((piVar1[1] ^ uVar11) != 0xfa50c32f) {
            plVar10[4] = *(ulonglong *)
                          (*(longlong *)(param_1 + 0x18) +
                          ((longlong)(int)(piVar1[1] ^ uVar11) ^ 0x5af3cd0U) * 8) ^
                         0x17c2856111b08173;
          }
          if ((*piVar1 + 0xc617c479U ^ uVar11) != 0xffffffff) {
            plVar10[1] = *(longlong *)
                          (*(longlong *)(param_1 + 0x18) +
                          (longlong)(int)(*piVar1 + 0xc617c479U ^ uVar11) * 8) + 0x7b0de6e70c06b3d8;
          }
          if ((piVar1[2] ^ uVar11) != 0xa1b22b0e) {
            plVar10[2] = *(longlong *)
                          (*(longlong *)(param_1 + 0x18) +
                          ((longlong)(int)(piVar1[2] ^ uVar11) ^ 0x5e4dd4f1U) * 8) +
                         0x1b89658f1f964a0c;
          }
          uVar9 = uVar9 + 1;
          *(uint *)(plVar10 + 5) = piVar1[5] + 0xce2556fdU ^ uVar11 ^ 0x3081751a;
          plVar10 = plVar10 + 7;
        } while ((int)uVar9 < iVar2);
      }
      *(longlong *)(param_1 + 0xa0) = lVar5;
    }
  }
  return;
}



/* ================= 0x18044B8FB ================= */
/* name   = FUN_18044b7f0 */
/* entry  = 18044b7f0 */
/* body   = 720 bytes */
/* sig    = undefined FUN_18044b7f0() */


void FUN_18044b7f0(longlong param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  longlong lVar4;
  undefined8 *puVar5;
  ulonglong uVar6;
  longlong lVar7;
  int iVar8;
  ulonglong uVar9;
  longlong lVar10;
  ulonglong *puVar11;
  uint uVar12;
  longlong lVar13;
  ulonglong *local_68;
  uint local_60;
  undefined1 local_58 [32];
  
  if (*(ushort *)(param_1 + 0x12a) != 0) {
    if (*(longlong *)(param_1 + 0x10) == 0) {
      uVar9 = (ulonglong)*(ushort *)(param_1 + 0x12a);
      lVar4 = FUN_1804f09a0(DAT_1899dbad0,uVar9,0x20);
      uVar6 = 0;
      if (uVar9 != 0) {
        do {
          puVar5 = (undefined8 *)(uVar6 * 0x20 + lVar4);
          if (puVar5 != (undefined8 *)0x0) {
            puVar5[3] = 0;
            *puVar5 = 0x6381435a10901789;
            puVar5[1] = 0x73ecc7d44725af21;
            puVar5[2] = 0x5a6601071b4f618a;
            *(undefined4 *)(puVar5 + 3) = 0x1c64e9e;
            *(undefined4 *)((longlong)puVar5 + 0x1c) = 0x7f804675;
          }
          uVar6 = uVar6 + 1;
        } while (uVar6 < uVar9);
      }
      uVar12 = (*(int *)(*(longlong *)(param_1 + 0xd0) + 0x1c) - *(int *)(param_1 + 200)) +
               0xaa6f650e;
      lVar10 = (longlong)(int)(*(ushort *)(param_1 + 0x12a) + uVar12);
      if ((int)uVar12 < lVar10) {
        puVar11 = (ulonglong *)(lVar4 + 8);
        lVar13 = 0;
        lVar10 = lVar10 - (int)uVar12;
        do {
          uVar6 = (ulonglong)uVar12;
          lVar7 = (DAT_188198e84 + -0x2f59fe76) + DAT_1899dbaf8;
          piVar1 = (int *)(lVar7 + uVar6 * 0xc);
          iVar8 = (int)(uVar6 * 0x7740eeff55f40540 + 0x49ed7f5afcc4af8 >> 0x11);
          iVar2 = (*(int *)(lVar7 + 4 + uVar6 * 0xc) - iVar8) + -0xf2a3d7f;
          if (iVar2 == -1) {
            lVar7 = 0;
          }
          else {
            lVar7 = *(longlong *)(PTR_PTR_1881a3628 + (longlong)iVar2 * 8);
          }
          puVar11[1] = lVar7 + 0x5a6601071b4f618a;
          uVar6 = FUN_18043ab50((piVar1[2] ^ 0x5daab140U) - iVar8);
          *puVar11 = uVar6 ^ 0x73ecc7d44725af21;
          puVar11[-1] = param_1 + 0x6381435a10901789;
          lVar7 = (*(longlong *)(param_1 + 0xd0) - ((longlong)DAT_188198e08 ^ 0x2b849db3U)) -
                  DAT_1899dbaf8;
          lVar7 = SUB168(SEXT816(-0x4de9bd37a6f4de9b) * SEXT816(lVar7),8) + lVar7;
          uVar3 = *(uint *)(lVar13 + *(longlong *)
                                      (PTR_DAT_1881a3618 +
                                      (longlong)((int)(lVar7 >> 6) - (int)(lVar7 >> 0x3f)) * 8));
          if ((int)uVar3 < 0) {
            local_60 = uVar3 & 0x7fffffff;
            local_68 = puVar11 + -1;
            FUN_180421430(&DAT_1899db520,local_58,&local_68,&local_68);
            uVar3 = 0xffffffff;
          }
          uVar12 = uVar12 + 1;
          *(uint *)((longlong)puVar11 + 0x14) = uVar3 + 0x7f804675;
          lVar13 = lVar13 + 4;
          *(uint *)(puVar11 + 2) = (*piVar1 - iVar8) + 0xfd930efcU ^ 0x1c64e9e;
          puVar11 = puVar11 + 4;
          lVar10 = lVar10 + -1;
        } while (lVar10 != 0);
      }
      *(longlong *)(param_1 + 0x10) = lVar4;
    }
    return;
  }
  *(undefined8 *)(param_1 + 0x10) = 0;
  return;
}



/* ================= 0x18044C03B ================= */
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



/* ================= 0x18044CBAF ================= */
/* name   = FUN_18044ca90 */
/* entry  = 18044ca90 */
/* body   = 600 bytes */
/* sig    = undefined FUN_18044ca90() */


void FUN_18044ca90(ulonglong param_1,undefined8 param_2)

{
  undefined8 *puVar1;
  longlong lVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  longlong lVar7;
  ulonglong uVar8;
  longlong lVar9;
  uint uVar10;
  ulonglong uVar11;
  longlong *plVar12;
  
  if (*(longlong *)(param_1 + 0x40) == 0) {
    if (*(undefined4 **)(param_1 + 0xc0) != (undefined4 *)0x0) {
      uVar6 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
      FUN_18044ca90(uVar6,param_2);
      FUN_18044c950(param_1);
      return;
    }
    if (*(short *)(param_1 + 0x126) != 0) {
      FUN_18044c400();
      uVar11 = (ulonglong)*(ushort *)(param_1 + 0x126);
      lVar7 = FUN_1804f09a0(DAT_1899dbad0,uVar11);
      uVar8 = 0;
      if (uVar11 != 0) {
        do {
          puVar1 = (undefined8 *)(lVar7 + uVar8 * 0x28);
          if (puVar1 != (undefined8 *)0x0) {
            puVar1[4] = 0;
            *puVar1 = 0x611cd27f76c29c9b;
            puVar1[1] = 0x316a29da26e27b29;
            puVar1[2] = 0x193676d401ac591b;
            puVar1[3] = 0x1b3786942518b0d3;
            *(undefined4 *)(puVar1 + 4) = 0x79f46a96;
            *(undefined4 *)((longlong)puVar1 + 0x24) = 0x7d7e5c29;
          }
          uVar8 = uVar8 + 1;
        } while (uVar8 < uVar11);
      }
      uVar10 = (*(int *)(*(longlong *)(param_1 + 0xd0) + 0x24) - *(int *)(param_1 + 200)) +
               0x97e219e0;
      iVar4 = *(ushort *)(param_1 + 0x126) + uVar10;
      if ((int)uVar10 < iVar4) {
        plVar12 = (longlong *)(lVar7 + 0x10);
        do {
          uVar8 = (ulonglong)uVar10;
          iVar3 = (int)(((uVar8 * 0x64d5 ^ 0x6d7b1f20) + 0x10eca71e) * 0x7737c996 >> 8) + 0x5505ff6b
          ;
          lVar9 = ((longlong)DAT_188198e28 ^ 0x3cb812e1U) + DAT_1899dbaf8;
          lVar2 = lVar9 + uVar8 * 0x14;
          lVar9 = FUN_18043ab50((*(uint *)(lVar9 + uVar8 * 0x14) ^ 0x5566c15d) + iVar3 * -0x1534fcf9
                               );
          plVar12[-2] = lVar9 + 0x611cd27f76c29c9b;
          plVar12[-1] = param_1 ^ 0x316a29da26e27b29;
          iVar5 = *(int *)(lVar2 + 4) + iVar3 * -0x1534fcf9;
          if (iVar5 != 0x4cf0c16a) {
            *plVar12 = *(longlong *)
                        (*(longlong *)(param_1 + 0x18) + (longlong)(iVar5 + -0x4cf0c16b) * 8) +
                       0x193676d401ac591b;
          }
          iVar5 = (*(uint *)(lVar2 + 0xc) ^ 0x128b6c5) + iVar3 * -0x1534fcf9;
          if (iVar5 != -1) {
            plVar12[1] = *(longlong *)(*(longlong *)(param_1 + 0x18) + (longlong)iVar5 * 8) +
                         0x1b3786942518b0d3;
          }
          uVar10 = uVar10 + 1;
          *(uint *)((longlong)plVar12 + 0x14) =
               (*(uint *)(lVar2 + 0x10) ^ 0x72d0b1bb) + iVar3 * -0x1534fcf9 + 0x7d7e5c29;
          *(uint *)(plVar12 + 2) =
               *(int *)(lVar2 + 8) + iVar3 * -0x1534fcf9 + 0x90d97b9aU ^ 0x79f46a96;
          plVar12 = plVar12 + 5;
        } while ((int)uVar10 < iVar4);
      }
      *(longlong *)(param_1 + 0x40) = lVar7;
    }
  }
  return;
}



/* ================= 0x180435E30 ================= */
/* name   = FUN_180435e30 */
/* entry  = 180435e30 */
/* body   = 115 bytes */
/* sig    = undefined FUN_180435e30() */


void FUN_180435e30(int param_1)

{
  int iVar1;
  undefined8 uVar2;
  longlong lVar3;
  undefined8 uVar4;
  
  lVar3 = (longlong)param_1;
  if (*(longlong *)(lVar3 * 8 + DAT_1899dbc00) == 0) {
    uVar4 = 0;
    uVar2 = uVar4;
    if (*(int *)(PTR_DAT_1881a3620 + lVar3 * 0xc + 4) != -1) {
      uVar2 = *(undefined8 *)
               (PTR_PTR_1881a35f8 + (longlong)*(int *)(PTR_DAT_1881a3620 + lVar3 * 0xc + 4) * 8);
    }
    iVar1 = *(int *)(PTR_DAT_1881a3620 + lVar3 * 0xc);
    if (iVar1 != -1) {
      uVar4 = *(undefined8 *)(PTR_PTR_1881a35f8 + (longlong)iVar1 * 8);
    }
    uVar2 = FUN_180435c60(*(int *)((longlong)(PTR_DAT_1881a3620 + lVar3 * 0xc) + 8),uVar2,uVar4);
    *(undefined8 *)(lVar3 * 8 + DAT_1899dbc00) = uVar2;
  }
  return;
}



/* ================= 0x180440139 ================= */
/* name   = FUN_180440120 */
/* entry  = 180440120 */
/* body   = 249 bytes */
/* sig    = undefined FUN_180440120() */


void FUN_180440120(void)

{
  int iVar1;
  undefined *puVar2;
  longlong lVar3;
  longlong lVar4;
  undefined8 uVar5;
  longlong lVar6;
  int iVar7;
  undefined8 uVar8;
  longlong local_38;
  undefined *local_30;
  undefined1 local_28 [32];
  
  iVar7 = 0;
  if (0 < (int)(DAT_1881a3630 ^ 0x421dd17c)) {
    lVar6 = 0;
    do {
      puVar2 = PTR_DAT_1881a3608;
      lVar4 = (longlong)*(int *)(PTR_DAT_1881a3608 + lVar6);
      lVar3 = *(longlong *)(lVar4 * 8 + DAT_1899dbc00);
      if (lVar3 == 0) {
        uVar5 = 0;
        uVar8 = 0;
        if (*(int *)(PTR_DAT_1881a3620 + lVar4 * 0xc + 4) != -1) {
          uVar5 = *(undefined8 *)
                   (PTR_PTR_1881a35f8 + (longlong)*(int *)(PTR_DAT_1881a3620 + lVar4 * 0xc + 4) * 8)
          ;
        }
        iVar1 = *(int *)(PTR_DAT_1881a3620 + lVar4 * 0xc);
        if (iVar1 != -1) {
          uVar8 = *(undefined8 *)(PTR_PTR_1881a35f8 + (longlong)iVar1 * 8);
        }
        lVar3 = FUN_180435c60(*(int *)((longlong)(PTR_DAT_1881a3620 + lVar4 * 0xc) + 8),uVar5,uVar8)
        ;
        *(longlong *)(lVar4 * 8 + DAT_1899dbc00) = lVar3;
      }
      local_30 = puVar2 + lVar6 + 4;
      local_38 = lVar3;
      FUN_180421080(&DAT_1899dba50,local_28,&local_38,&local_38);
      iVar7 = iVar7 + 1;
      lVar6 = lVar6 + 0x10;
    } while (iVar7 < (int)(DAT_1881a3630 ^ 0x421dd17c));
  }
  return;
}



/* ================= 0x180437660 ================= */
/* name   = FUN_180437660 */
/* entry  = 180437660 */
/* body   = 642 bytes */
/* sig    = undefined FUN_180437660() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_180437660(undefined4 param_1,undefined8 *param_2)

{
  int iVar1;
  uint uVar2;
  byte bVar3;
  char cVar4;
  ulonglong uVar5;
  ulonglong uVar6;
  longlong lVar7;
  longlong *plVar8;
  ulonglong uVar9;
  ulonglong uVar10;
  undefined8 *puVar11;
  undefined4 local_38 [2];
  undefined8 local_30;
  undefined8 local_28;
  
  local_30 = *param_2;
  local_28 = param_2[1];
  local_38[0] = param_1;
  uVar5 = FUN_1804ea180(&DAT_1899dba51,local_38);
  uVar5 = DAT_1899dba58 & uVar5;
  uVar9 = 0;
  uVar10 = DAT_1899dba58;
  while( true ) {
    while( true ) {
      plVar8 = (longlong *)((uVar5 >> 6) * 0x20 + _DAT_1899dba78);
      uVar6 = 1L << ((byte)uVar5 & 0x3f);
      if ((plVar8[1] & uVar6) == 0) break;
      bVar3 = FUN_180415ac0(uVar6 - 1 & plVar8[1]);
      puVar11 = (undefined8 *)((ulonglong)bVar3 * 0x10 + *plVar8);
      cVar4 = FUN_1804ea160(&DAT_1899dba52,local_38,*puVar11);
      if (cVar4 != '\0') {
        lVar7 = (uVar5 >> 6) * 0x20 + DAT_1899dba60;
        goto LAB_180437765;
      }
      uVar9 = uVar9 + 1;
      uVar5 = uVar5 + uVar9 & DAT_1899dba58;
      uVar10 = DAT_1899dba58;
    }
    if (((plVar8[2] & uVar6) == 0) || (DAT_1899dba80 <= uVar9)) break;
    uVar9 = uVar9 + 1;
    uVar5 = uVar5 + uVar9 & uVar10;
  }
  puVar11 = (undefined8 *)0x0;
  lVar7 = DAT_1899dba68;
LAB_180437765:
  if (((lVar7 - DAT_1899dba60 & 0xffffffffffffffe0U) + DAT_1899dba60 == DAT_1899dba68) &&
     (puVar11 == (undefined8 *)0x0)) {
    local_30 = FUN_18043a520(*param_2);
    local_28 = FUN_18043a520(param_2[1]);
    uVar5 = FUN_1804ea180(&DAT_1899dba51,local_38);
    uVar5 = uVar5 & DAT_1899dba58;
    uVar9 = 0;
    uVar10 = DAT_1899dba58;
    while( true ) {
      while( true ) {
        plVar8 = (longlong *)((uVar5 >> 6) * 0x20 + _DAT_1899dba78);
        uVar6 = 1L << ((byte)uVar5 & 0x3f);
        if ((plVar8[1] & uVar6) == 0) break;
        bVar3 = FUN_180415ac0(plVar8[1] & uVar6 - 1);
        puVar11 = (undefined8 *)((ulonglong)bVar3 * 0x10 + *plVar8);
        cVar4 = FUN_1804ea160(&DAT_1899dba52,local_38,*puVar11);
        if (cVar4 != '\0') {
          lVar7 = (uVar5 >> 6) * 0x20 + DAT_1899dba60;
          goto LAB_180437878;
        }
        uVar9 = uVar9 + 1;
        uVar5 = uVar5 + uVar9 & DAT_1899dba58;
        uVar10 = DAT_1899dba58;
      }
      if (((plVar8[2] & uVar6) == 0) || (DAT_1899dba80 <= uVar9)) break;
      uVar9 = uVar9 + 1;
      uVar5 = uVar5 + uVar9 & uVar10;
    }
    puVar11 = (undefined8 *)0x0;
    lVar7 = DAT_1899dba68;
LAB_180437878:
    if (((lVar7 - DAT_1899dba60 & 0xffffffffffffffe0U) + DAT_1899dba60 == DAT_1899dba68) &&
       (puVar11 == (undefined8 *)0x0)) {
      return 0;
    }
  }
  iVar1 = *(int *)puVar11[1];
  if (iVar1 != -1) {
    return *(undefined8 *)(PTR_PTR_188139728 + (longlong)iVar1 * 8);
  }
  uVar2 = ((int *)puVar11[1])[1];
  if ((DAT_188139730 ^ 0x75f0cd0b) <= uVar2) {
    return 0;
  }
  return *(undefined8 *)(PTR_DAT_188139740 + (longlong)(int)uVar2 * 8);
}



/* ================= 0x180440120 ================= */
/* name   = FUN_180440120 */
/* entry  = 180440120 */
/* body   = 249 bytes */
/* sig    = undefined FUN_180440120() */


void FUN_180440120(void)

{
  int iVar1;
  undefined *puVar2;
  longlong lVar3;
  longlong lVar4;
  undefined8 uVar5;
  longlong lVar6;
  int iVar7;
  undefined8 uVar8;
  longlong local_38;
  undefined *local_30;
  undefined1 local_28 [32];
  
  iVar7 = 0;
  if (0 < (int)(DAT_1881a3630 ^ 0x421dd17c)) {
    lVar6 = 0;
    do {
      puVar2 = PTR_DAT_1881a3608;
      lVar4 = (longlong)*(int *)(PTR_DAT_1881a3608 + lVar6);
      lVar3 = *(longlong *)(lVar4 * 8 + DAT_1899dbc00);
      if (lVar3 == 0) {
        uVar5 = 0;
        uVar8 = 0;
        if (*(int *)(PTR_DAT_1881a3620 + lVar4 * 0xc + 4) != -1) {
          uVar5 = *(undefined8 *)
                   (PTR_PTR_1881a35f8 + (longlong)*(int *)(PTR_DAT_1881a3620 + lVar4 * 0xc + 4) * 8)
          ;
        }
        iVar1 = *(int *)(PTR_DAT_1881a3620 + lVar4 * 0xc);
        if (iVar1 != -1) {
          uVar8 = *(undefined8 *)(PTR_PTR_1881a35f8 + (longlong)iVar1 * 8);
        }
        lVar3 = FUN_180435c60(*(int *)((longlong)(PTR_DAT_1881a3620 + lVar4 * 0xc) + 8),uVar5,uVar8)
        ;
        *(longlong *)(lVar4 * 8 + DAT_1899dbc00) = lVar3;
      }
      local_30 = puVar2 + lVar6 + 4;
      local_38 = lVar3;
      FUN_180421080(&DAT_1899dba50,local_28,&local_38,&local_38);
      iVar7 = iVar7 + 1;
      lVar6 = lVar6 + 0x10;
    } while (iVar7 < (int)(DAT_1881a3630 ^ 0x421dd17c));
  }
  return;
}



