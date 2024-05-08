% 人数を定義
numPeople = 100000;

% 構造体の配列を初期化
people = struct('name', {}, 'age', {});

% 各人物のデータを挿入
for i = 1:numPeople
    % 新しい構造体を作成
    newPerson.name = ['Person' num2str(i)];
    newPerson.age = randi([20, 60]);  % 20歳から60歳の範囲でランダムな年齢

    % 配列に新しい構造体を追加
    people(end+1) = newPerson;
end

% 確認のため、最初と最後のデータを表示
disp(people(1));
disp(people(end));
