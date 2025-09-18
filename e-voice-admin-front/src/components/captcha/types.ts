/**
 * @author Awen
 * @Date 2024/06/01
 * @Email wengaolng@gmail.com
 */
export interface CaptchaConfig {
  width?: number; // 底图宽
  height?: number; // 底图高
  rotateSize?: number; // 旋转图宽高
  thumbWidth?: number; // 缩略图宽
  thumbHeight?: number; // 缩略图高
  verticalPadding?: number;
  horizontalPadding?: number;
  showTheme?: boolean;
}

export const defaultConfig = (): CaptchaConfig => ({
  width: 310,
  height: 155,
  rotateSize: 155,
  thumbWidth: 150,
  thumbHeight: 40,
  verticalPadding: 16,
  horizontalPadding: 12,
  showTheme: true
});

export interface CaptchaData {
  thumbX: number;
  thumbY: number;
  thumbWidth: number;
  thumbHeight: number;
  image: string;
  thumb: string;
  angle: number;
}

export interface CaptchaEvent {
  rotate?: (angle: number) => void;
  refresh?: () => void;
  close?: () => void;
  move?: (x: number, y: number) => void;
  click?: (x: number, y: number) => void;
  confirm?: (
    data: { angle: number } | { position: Point } | { points: Array<Point> },
    clear: (fn: void) => void
  ) => void;
}

export interface Point {
  key?: number;
  index?: number;
  x: number;
  y: number;
}
