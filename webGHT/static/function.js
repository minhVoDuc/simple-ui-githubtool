/*-------- Create Repo ---------------*/
// get file 
var jsonList
$(document).on('change', '.add-repolist', function(event) {
  var reader = new FileReader();

  reader.onload = function(event) {
    jsonList = JSON.parse(event.target.result);
    console.log(jsonList);
  }

  reader.readAsText(event.target.files[0]);
});

// append to form
$(document).on('click', '.btn-upload-jsonlist', function(e) {
  for (var i=0; i<jsonList.length; i++){
    console.log(jsonList.length)
    repo = jsonList[i];
    var currentVal = $("#json-list").val();
    if (i>0) {
      currentVal = currentVal + ",\n";
    }
    $("#json-list").val(currentVal + JSON.stringify(repo, undefined, 2));
  }
});

// additional option
$(document).on('change', '#readme-switch', function(e) {
  var value = $('#readme-switch').is(':checked');
  console.log(value)
  if (value) {
    $('#create-repo-addition').removeClass('d-none');
    $('#create-repo-addition').addClass('d-block');
  }
  else {
    $('#create-repo-addition').removeClass('d-block');
    $('#create-repo-addition').addClass('d-none');
  }
})
/*----------- Custom Display -------------*/