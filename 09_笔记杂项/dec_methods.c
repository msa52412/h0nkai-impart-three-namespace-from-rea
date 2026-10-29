// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x180436810 ================= */
/* name   = FUN_180436810 */
/* entry  = 180436810 */
/* body   = 265 bytes */
/* sig    = undefined FUN_180436810() */


longlong FUN_180436810(undefined8 param_1)

{
  longlong lVar1;
  char cVar2;
  longlong lVar3;
  longlong lVar4;
  longlong lVar5;
  undefined1 auStackX_11 [7];
  
  lVar5 = DAT_1899db868 * 0x38 + DAT_1899db860;
  lVar3 = (lVar5 - DAT_1899db860) / 0x38;
  lVar4 = DAT_1899db860;
  while (lVar1 = lVar3, 0 < lVar1) {
    lVar3 = lVar1 / 2;
    cVar2 = FUN_1804ea220(auStackX_11,*(undefined8 *)(lVar3 * 0x38 + 0x30 + lVar4),param_1);
    if (cVar2 != '\0') {
      lVar4 = lVar4 + 0x38 + lVar3 * 0x38;
      lVar3 = lVar1 + (-1 - lVar3);
    }
  }
  if ((lVar4 == lVar5) ||
     (cVar2 = FUN_1804ea260(*(undefined8 *)(lVar4 + 0x30),param_1), cVar2 == '\0')) {
    lVar4 = lVar5;
  }
  if (lVar4 == DAT_1899db868 * 0x38 + DAT_1899db860) {
    lVar4 = 0;
  }
  return lVar4;
}



/* ================= 0x18044b7f0 ================= */
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



