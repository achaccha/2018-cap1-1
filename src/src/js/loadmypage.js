var web3Provider;

var contracts = {};
var tokenCount;

if(typeof web3 !== "undefined"){
    web3Provider = web3.currentProvider;
}else {
    web3Provider = new web3Provider.providers.HttpProvider("http://localhost:7545");
}
web3 = new Web3(web3Provider);

(function(){

    $.getJSON("OpenJournal.json", function(data){
        var Artifact = data;
        contracts.OpenJournal = TruffleContract(Artifact);
        contracts.OpenJournal.setProvider(web3Provider);
        contracts.OpenJournal.deployed().then(function(instance){
		    var user = getUserAccount();
            var res = instance.balanceOf(user);
		    var id = instance.getUserNumber({from : user});
		    console.log(id);
		    id.then(function(result){
			    document.getElementById("blockchain_id").innerText = parseInt(result['c'][0]);
		    });
            res.then(function(result){
			    document.getElementById("tokenNum").innerText = (parseFloat(result['c'][0]/10000));
		    });
            // instance.getUserSubscribedJournals({from: user})
            // .then(function(res){
            //     for(var i = 0; i < res.length; i++){
            //         subscribeList.push(parseInt(res[i]['c']));
            //     }
            //     subscribeListCount = subscribeList.length;
            // });
            // instance.getUserRegistedJournals({from: user})
            // .then(function(res){
            //     for(var i = 0; i < res.length; i++){
            //         registList.push(parseInt(res[i]['c']));
            //     }
            //     registListCount = registList.length;
            // });
        });
    })
})();

function getUserAccount(){
    var account;
    account = web3.eth["coinbase"];
    return account;
}
