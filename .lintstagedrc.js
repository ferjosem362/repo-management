// Unfortunately we need this file because lint-staged 10.5.4
module.exports = {
    // C#
    '*.cs': ['dotnet format --include'],
    // SCSS
    '*.scss': ['sass-lint -v -q'],
    // JS
    '*.(m)js': ['eslint'],
}