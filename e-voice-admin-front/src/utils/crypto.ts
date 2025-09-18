import CryptoJS from 'crypto-js';

const CryptoSecret = '_CryptoJSSecret_';

/**
 * 加密数据
 *
 * @param data - 数据
 * @param secret - 密钥
 */
export function encryptBase64(data: any, secret?: string) {
  const plaintext = JSON.stringify(data);

  // 确保密钥为16字节
  if (secret && secret.length >= 16) {
    // eslint-disable-next-line no-param-reassign
    secret = secret.substring(0, 16);
  } else {
    // eslint-disable-next-line no-param-reassign
    secret = CryptoSecret;
  }

  const key = CryptoJS.enc.Utf8.parse(secret);

  // 生成随机 IV
  const iv = CryptoJS.lib.WordArray.random(16);

  const encrypted = CryptoJS.AES.encrypt(plaintext, key, {
    iv,
    padding: CryptoJS.pad.Pkcs7,
    mode: CryptoJS.mode.CBC
  });

  // 手动拼接 IV 和密文的 Base64
  const cipherHex = CryptoJS.enc.Base64.stringify(
    CryptoJS.lib.WordArray.create(iv.words.concat(encrypted.ciphertext.words))
  );

  return { cipherHex, secret };
}

/**
 * 解密数据
 *
 * @param cipherText - 密文
 * @param secret - 密钥
 */
export function decrypto(cipherText: string, secret?: string) {
  const bytes = CryptoJS.AES.decrypt(cipherText, secret || CryptoSecret);
  const originalText = bytes.toString(CryptoJS.enc.Utf8);
  if (originalText) {
    return JSON.parse(originalText);
  }
  return null;
}
