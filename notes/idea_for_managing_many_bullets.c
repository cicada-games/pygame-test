/**
* Just an idea i had for managing many bullets. don't know if this will work for the cicada game,
* but i though i should share it either way
* 
* The idea here is the object pool pattern. You basically have a pre-instantiated array of your objects. The objects can either contain an activeFlag, 
* or there can be a separate integer value to be used as a bitmask that keeps track of the active objects. The active objects will be updated and rendered. 
* I'm going to show an example of the bitmask way.
*
* an index in the pool is the bulletId. The bulletId will correspond to a digit in the bitmask. 
*
* It's a pattern that can be used when needed to "Create" and "destroy" objects many times.
* I've heard it's used in bullet-hell and shooter type games
*/

#define MAX_NUM_BULLETS 64

// assuming we have these data structures somewhere
typedef struct {
    Vector_f velocity;
    Position_f position;
} Bullet;

// the idea here is the object pool pattern
// just an array of bullets
Bullet *bulletPool; 

// 1 = 0b000..1
#define BULLET_ACTIVE_FLAG 1 
uint64_t bulletActiveMask = 0b0; // multiple bitmasks can be used to track bulletPools that are larger. 

Bullet *bulletPoolInit( ) {
    Bullet *bulletPool = (Bullet *)malloc( sizeof(Bullet) * MAX_NUM_BULLETS );
    Bullet zeroBullet;
    zeroBullet.position.x = 0;
    zeroBullet.position.y = 0;
    zeroBullet.velocity.x = 0;
    zeroBullet.velocity.y = 0;
    for( int i = 0; i < MAX_NUM_BULLETS; i++ ) {
        bulletPool[ i ] = zeroBullet;
    }
    // just zero out all the bullets in the pool for initialization.
    // bulletActiveMask is already set to all zeros
    return bulletPool;
}

// returns newly created bullet id if needed by caller
unsigned int fireBullet(Position_f initialPos, Vector_f initialVel ) {
    unsigned int bulletId = 65; //invalid
    // this keeps looking for the first bit that is 0. This means an unactivated bullet that can become active.
    for( int i = 0; i < 64; i++ ) {
        if( ( bulletActiveMask << i ) & 0b0 ) {
            bulletId = i;
            break;
        }
    }

    bulletActiveMask |= ( 0b1 << bulletId ); // sets the bit correlating to the bullet id to active (1)
    bulletPool[ bulletId ].position = initialPos;
    bulletPool[ bulletId ].velocity = initialVel;

    return bulletId;

    // now that the bitmask is set for this bullet id, it will be processes during the bulletsUpdate() function
}

void deactivateBullet( unsigned int bulletId ) {
    // this bullet will not be processed or rendered anymore
    // AND it will be able to be written over when a new bullet is fired
    bulletActiveMask ^= ( 0b1 << bulletId );
}

void bulletsUpdate( ) {
    for( int i = 0; i < MAX_NUM_BULLETS; i++ ) {
        // bullet is inactive
        if( bulletActiveMask & ( 0b1 < i ) == 0b0 ) {
            continue;
        }
        // bullet is active
        //.. process bullet
        // if bullet dies?
        //      deactivateBullet( i )
    }
}
