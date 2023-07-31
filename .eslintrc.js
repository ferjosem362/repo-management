// eslint configuration
module.exports = {
    env: {
      browser: true,
      jest: true,
    },
    extends: [
       // ES6 https://www.npmjs.com/package/eslint-config-airbnb-base
      'airbnb-base',
      // jest
      'plugin:jest/recommended',
      // Sky standard configuration for JS
      '@sky-uk/eslint-config-sky/packages/eslint-config-sky',
      // standard prettier
      'prettier',
      // recommended for Cypress
      'plugin:cypress/recommended',
    ],
    globals: {
      lng: true,
      FeatureFlags: true,
    },
    parserOptions: {
      ecmaVersion: 12,
      sourceType: 'module',
    },
    plugins: ['prettier'],
    // updated rules
    rules: {
      'prettier/prettier': ['error', {}],
      'import/no-extraneous-dependencies': ['error', { devDependencies: true }],
      'no-param-reassign': [2, { props: false }],
      'import/no-relative-packages': [1, {}],
      'jest/valid-expect-in-promise': 'warn',
    },
    ignorePatterns: ['.cache', 'coverage', 'dist', 'node_modules', 'tools/fixtures/'],
  };