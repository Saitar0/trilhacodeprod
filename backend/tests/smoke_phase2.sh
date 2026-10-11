U=http://localhost:8001/api
TID=6acb0b40ef07136c920e83c2
J='-H Content-Type:application/json'
curl -s -c /tmp/a.txt -X POST $U/auth/login $J -d '{"email":"admin@trilhacode.dev","password":"Admin@123"}' >/dev/null
curl -s -c /tmp/s.txt -X POST $U/auth/login $J -d '{"email":"aluno@trilhacode.dev","password":"Aluno@123"}' >/dev/null
echo "--publish v2 (baseline)"; curl -s -b /tmp/a.txt -X POST $U/tracks/$TID/publish $J -d '{"note":"baseline"}' | head -c 80; echo
curl -s -b /tmp/a.txt -X PUT $U/tracks/$TID $J -d '{"settings":{"enforce_prerequisites":true,"unlock_strategy":"free","visual_style":"default"}}' | head -c 60; echo
for R in 6acb0b40ef07136c920e83ec 6acb0b40ef07136c920e83ed 6acb0b40ef07136c920e83ee 6acb0b40ef07136c920e83ef; do curl -s -b /tmp/a.txt -X PUT $U/relations/$R $J -d '{"enforced":true}' >/dev/null; done
echo "--cycle"; curl -s -b /tmp/a.txt -X POST $U/relations $J -d '{"node_id":"6acb0b40ef07136c920e83c5","target_id":"6acb0b40ef07136c920e83e7","type":"prerequisite"}'; echo
echo "--ancestor"; curl -s -b /tmp/a.txt -X POST $U/relations $J -d '{"node_id":"6acb0b40ef07136c920e83c5","target_id":"6acb0b40ef07136c920e83c4","type":"prerequisite"}'; echo
echo "--student locks"; curl -s -b /tmp/s.txt $U/progress/tracks/$TID | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['locks'])"
echo "--locked node"; curl -s -b /tmp/s.txt $U/nodes/6acb0b40ef07136c920e83e7 | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['lock'], len(d['blocks']))"
echo "--complete locked"; curl -s -b /tmp/s.txt -X POST $U/progress $J -d '{"node_id":"6acb0b40ef07136c920e83e7","status":"completed"}'; echo
echo "--add exercise"; BID=$(curl -s -b /tmp/a.txt -X POST $U/blocks $J -d '{"node_id":"6acb0b40ef07136c920e83c5","type":"exercise_open","title":"Explique tipos","data":{"prompt":"Explique a diferença entre tipos primitivos e de referência.","criteria":["Define primitivos","Define referência","Dá exemplo"],"allow_resubmit":true,"grading":"manual"}}' | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])"); echo $BID
curl -s -b /tmp/s.txt -X PUT $U/submissions/draft $J -d "{\"block_id\":\"$BID\",\"answer\":{\"text\":\"rascunho\"}}" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['status'],d['attempt'])"
SID=$(curl -s -b /tmp/s.txt -X POST $U/submissions/submit $J -d "{\"block_id\":\"$BID\",\"answer\":{\"text\":\"Primitivos guardam valor; referência guarda endereço.\"}}" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['id'])"); echo SID=$SID
curl -s -b /tmp/a.txt "$U/submissions?status=submitted" | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d['items']),d['counts'])"
curl -s -b /tmp/a.txt -X POST $U/submissions/$SID/claim | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])"
curl -s -b /tmp/s.txt -X PUT $U/submissions/draft $J -d "{\"block_id\":\"$BID\",\"answer\":{\"text\":\"x\"}}"; echo
curl -s -b /tmp/a.txt -X POST $U/submissions/$SID/grade $J -d '{"result":"returned","feedback":"Faltou exemplo","criteria":[{"criterion":"Dá exemplo","met":false,"comment":"sem exemplo"}]}' | python3 -c "import sys,json;print(json.load(sys.stdin)['status'])"
curl -s -b /tmp/s.txt -X POST $U/submissions/submit $J -d "{\"block_id\":\"$BID\",\"answer\":{\"text\":\"Agora com exemplo: int vs objeto\"}}" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['status'],d['attempt'])"
curl -s -b /tmp/a.txt -X POST $U/submissions/$SID/grade $J -d '{"result":"approved","feedback":"ok"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['grading']['result'])"
echo "--student forbidden list"; curl -s -o /dev/null -w "%{http_code}\n" -b /tmp/s.txt $U/submissions
echo "--notes/reviews"; curl -s -b /tmp/s.txt -X PUT $U/notes $J -d '{"node_id":"6acb0b40ef07136c920e83c5","body":"minha nota"}' | head -c 80; echo
curl -s -b /tmp/s.txt -X POST $U/reviews $J -d '{"node_id":"6acb0b40ef07136c920e83c5","when":"suggested"}' | head -c 120; echo
RID=$(curl -s -b /tmp/s.txt $U/reviews | python3 -c "import sys,json;d=json.load(sys.stdin);print(d[0]['id'], d[0]['node_title'])"); echo $RID
echo "--compare"; V=$(curl -s -b /tmp/a.txt $U/tracks/$TID/versions | python3 -c "import sys,json;d=json.load(sys.stdin);print(d[0]['id'], d[0]['version'])"); echo $V
VID=$(echo $V | cut -d' ' -f1); VN=$(echo $V | cut -d' ' -f2)
curl -s -b /tmp/a.txt "$U/tracks/$TID/compare?base=$VID&target=current" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['total_changes'], len(d['blocks']['added']), len(d['relations']['changed']), d['track'])"
