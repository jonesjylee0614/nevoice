import { defineConfig } from '@soybeanjs/eslint-config';

export default defineConfig(
  {
    vue: true,
    ignores: [
      'node_modules/**', // 忽略 node_modules 文件夹
      'dist/**', // 忽略 dist 文件夹
      'build/**', // 忽略 build 文件夹
      'public/**' // 忽略 public 文件夹
    ]
  },
  {
    rules: {
      'n/prefer-global/process': 'off',
      'vue/no-undef-properties': 'off',
      'no-var': 'off',
      'max-params': 'off',
      semi: ['error'],
      complexity: 'off',
      'max-depth': 'off',
      'guard-for-in': 'off',
      'symbol-description': 'off',
      'default-param-last': 'off',
      'no-async-promise-executor': 'off',
      'no-nested-ternary': 'off',
      '@typescript-eslint/ban-ts-comment': 'off',
      'no-console': 'off',
      'logical-assignment-operators': 'off',
      'no-continue': 'off',
      'no-plusplus': 'off',
      'func-names': 'off',
      'no-multi-assign': 'off',
      'no-unmodified-loop-condition': 'off',
      '@typescript-eslint/no-non-null-asserted-optional-chain': 'off',
      eqeqeq: 'off',
      'vue/define-props-declaration': 'off',
      'vue/no-static-inline-styles': 'off',
      'no-param-reassign': 'off',
      'vue/multi-word-component-names': 'off',
      'vue/no-multiple-template-root': 'off',
      'vue/define-emits-declaration': 'off',
      'no-underscore-dangle': 'off',
      'consistent-return': 'off',
      '@typescript-eslint/no-invalid-void-type': 'off',
      '@typescript-eslint/no-dynamic-delete': 'off',
      '@typescript-eslint/no-shadow': 'off',
      '@typescript-eslint/no-unused-expressions': 'off',
      'class-methods-use-this': 'off',
      'vue/custom-event-name-casing': 'off',
      'vue/no-v-model-argument': 'off',
      'vue/block-order': [
        'error',
        {
          order: ['template', 'script', 'style']
        }
      ],
      // 确保 template 标签在 script 标签之前
      'vue/component-tags-order': [
        'error',
        {
          order: ['template', 'script', 'style']
        }
      ],
      'no-restricted-syntax': 'off',
      'vue/component-name-in-template-casing': [
        'warn',
        'PascalCase',
        {
          registeredComponentsOnly: false,
          ignores: ['/^icon-/']
        }
      ],
      '@typescript-eslint/no-use-before-define': 'off',
      '@typescript-eslint/no-unused-vars': 'off'
    }
  }
);
