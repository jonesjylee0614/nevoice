package cryptox

import "golang.org/x/crypto/bcrypt"

// bcrypt加密密码
func PwdHash(password string) string {
	bytes, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes)
}

// 检查密码是否一致
func CheckPwdHash(password, hash string) bool {
	return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) == nil
}
